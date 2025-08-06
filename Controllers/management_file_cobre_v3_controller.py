from flask import jsonify
from Database.database import Session
import logging
import uuid
from datetime import datetime
import os
import io
from flask import send_file
import pandas as pd
import traceback

from Models.counter_party import CounterParty as CounterPartyModel
from Controllers.counter_party_controller import CounterParty as CounterPartyController
from Controllers.data_load_controller import DataLoad as DataLoadController
from Controllers.debit_register_controller import (
    DebitRegister as DebitRegisterController,
)

# Cobre V3
from Controllers.cobre_v3_CP_controller import (
    CobreV3CounterParty as CobreV3CounterPartyController,
)
from Controllers.cobre_v3_DDR_controller import (
    CobreV3DirectDebit as CobreV3DirectDebitController,
)

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
SOURCE_ID = "acc_znB5gf46CU"


class ManagementFileCobreV3Controller:

    def __init__(self):
        self.session = Session()
        self.counterparty = CounterPartyController()
        self.debit_register = DebitRegisterController()
        self.data_load = DataLoadController()
        self.cobre_v3_cp = CobreV3CounterPartyController()
        self.cobre_v3_ddr = CobreV3DirectDebitController()

    def __del__(self):
        self.session.close()

    # funcion leer archivo cvs
    def read_file_csv_cobre_v3(self, data_csv):
        try:

            # ---------- GENERA UN ID DE CARGUE ---------
            id_data_load = generator_id("load_00", 1)

            # ---------- GUARDA UN REGISTRO DE CARGUE --------
            self.data_load.set_data_load(id_data_load, "PENDING")

            # ----------BUSQUEDA DE COUNTERPARTIES EXISTENTES------------
            filter_cp = self.cobre_v3_cp.filter_counter_party_id_number(data_csv)

            cp_data_save = []
            new_ddr = []
            index_count = 0

            for cp_csv in data_csv:

                # GENERA SIEMPRE UN DDR SIN IMPORTAR SI EL CP EXISTE O NO EN COBRE
                new_ddr.append(
                    {
                        "id_cp": None,
                        "fk_data_load": id_data_load,
                        "beneficiary_institution": cp_csv["beneficiary_institution"],
                        "counterparty_id_number": cp_csv["counterparty_id_number"],
                        "account_number": cp_csv["account_number"],
                        # --DIRECT DEBIT--
                        "destination_id": SOURCE_ID,
                        "registration_description": "Direct",
                    },
                )

                # Busca el CP
                cp_id = next(
                    (
                        f
                        for f in filter_cp
                        if f is not None
                        and f.get("metadata", {}).get("beneficiary_institution")
                        == cp_csv.get("beneficiary_institution")
                        and f.get("metadata", {}).get("account_number")
                        == cp_csv.get("account_number")
                        and f.get("metadata", {}).get("counterparty_id_number")
                        == cp_csv.get("counterparty_id_number")
                    ),
                    None,
                )

                if cp_id is not None:
                    new_ddr[index_count]["id_cp"] = cp_id["id"]
                else:
                    cp_data_save.append(cp_csv)
                index_count += 1

            # -------------- GUARDA COUNTER PARTIES EN COBRE V3 ---------------
            counter_parties_saved = []
            if len(cp_data_save) > 0:
                counter_parties_saved = self.cobre_v3_cp.send_all_counterparties(
                    body_counter_party(cp_data_save)
                )

                # --------- COUNTER PARTYS GUARDADOS EN LA BD LOCAL ----------
                self.counterparty.set_counter_party_cobre_body(
                    counter_parties_saved, id_data_load
                )

            # # # ----------- LE ASIGNA CADA ID CP A CADA DRR ----------------
            for ddr in filter(lambda d: d.get("id_cp") is None, new_ddr):
                cp = next(
                    (
                        cp_saved
                        for cp_saved in counter_parties_saved
                        if cp_saved.get("metadata", {}).get("counterparty_id_number")
                        == ddr.get("counterparty_id_number")
                        and cp_saved.get("metadata", {}).get("beneficiary_institution")
                        == ddr.get("beneficiary_institution")
                        and cp_saved.get("metadata", {}).get("account_number")
                        == ddr.get("account_number")
                    ),
                    None,
                )
                if cp is not None:
                    ddr["id_cp"] = cp.get("id")

            # -------- GUARDA LOS DIRECT DEBIT EN COBRE V3 -----------
            direct_debit_saved = self.cobre_v3_ddr.send_all_direct_debit(new_ddr)
            logger.debug("PAYLOAD DDR COBRE V3 GUARDADO")

            # -------- GUARDA LOS DIRECT DEBIT EN LA BD LOCAL ---------
            self.debit_register.set_list_debit_registration_cobre_v3(
                compare_ddr(direct_debit_saved, new_ddr)
            )

            return (
                jsonify(
                    {
                        "message": "Archivo procesado exitosamente",
                        "CP Creados": counter_parties_saved,
                        "DDR Creados": new_ddr,
                    }
                ),
                200,
            )

        except FileNotFoundError:
            return (
                jsonify({"error": "El archivo no fue encontrado."}),
                404,
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "error": f"Error procesando el archivo: {str(e)}",
                        "traceback": f"Error {traceback.extract_tb(e.__traceback__)}",
                    }
                ),
                500,
            )

    def export_file_csv_cobre_v3_ddr(self, created_at):
        try:

            # Consulta todos los DDR cargados en {created_at}
            ddr_created_at = self.debit_register.get_debit_register_create_at(
                created_at
            )
            df = pd.DataFrame(ddr_created_at)

            # Generar archivo Excel en memoria
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)

            # Nombre dinámico
            filename = f"direct_debit_{created_at}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            return {"error": str(e)}, 500


def body_counter_party(data_csv):
    counter_parties = []
    for row in data_csv:
        number = row["counterparty_phone"]
        number_replace = number.replace("\u202a", "").replace("\u202c", "")
        counter_parties.append(
            {
                "geo": row["geo"],
                "type": row["type"],
                "alias": row["alias"],
                "metadata": {
                    "account_number": row["account_number"],
                    "counterparty_fullname": row["counterparty_fullname"],
                    "counterparty_id_type": row["counterparty_id_type"],
                    "counterparty_id_number": row["counterparty_id_number"],
                    "counterparty_phone": number_replace,
                    "counterparty_email": row["counterparty_email"],
                    "beneficiary_institution": row["beneficiary_institution"],
                },
            }
        )
    return counter_parties


def compare_ddr(direct_debit_saved, new_ddr):
    payload_ddr = []
    for ddr_saved in direct_debit_saved:

        ddr_find = next(
            (
                ddr_filter
                for ddr_filter in new_ddr
                if ddr_filter["id_cp"] == ddr_saved["id_cp"]
            ),
            None,
        )

        # PAYLOAD DE REGISTER DEBIT ACTUALIZADO con ESTADO REGISTERD PARA EL MM
        payload_ddr.append(
            {
                "id": ddr_saved["id"],
                "destination_id": SOURCE_ID,
                "registration_description": ddr_saved["registration_description"],
                # BD local
                "fk_id_counterparty": ddr_saved["id_cp"],  # Id del counter party
                "fk_data_load": ddr_find["fk_data_load"],  # Id del cargue
                "state_local": "01",
                "state": ddr_saved["status"]["state"],
                "code": ddr_saved["status"]["code"],
                "description": ddr_saved["status"]["description"],
            },
        )
    return payload_ddr


def generator_id(test, index):
    prefij = f"{test}{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
