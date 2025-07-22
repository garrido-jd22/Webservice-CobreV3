from flask import jsonify
from Database.database import Session
import logging
import uuid
from datetime import datetime
import os
import pandas as pd

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

            for cp_csv in data_csv:

                cp_id = next(
                    (
                        f
                        for f in filter_cp
                        if f["counterparty_id_number"]
                        == cp_csv["counterparty_id_number"]
                    ),
                    None,
                )

                data_exist = cp_id["exist"]
                data_exist_code_bank = [
                    cp_exist
                    for cp_exist in data_exist
                    if cp_exist["metadata"]["beneficiary_institution"]
                    == cp_csv["beneficiary_institution"]
                ]

                # GENERA SIEMPRE UN DDR SIN IMPORTAR SI EL CP EXISTE O NO EN COBRE
                new_ddr.append(
                    {
                        "id_cp": "Pennding",
                        "beneficiary_institution": cp_csv["beneficiary_institution"],
                        "counterparty_id_number": cp_csv["counterparty_id_number"],
                        "fk_data_load": id_data_load,
                        # --DIRECT DEBIT--
                        "destination_id": SOURCE_ID,
                        "registration_description": "Direct",
                        # ---
                        "account_number": cp_csv["account_number"],
                    },
                )

                if len(data_exist) == 0 or (
                    len(data_exist) > 0 and len(data_exist_code_bank) == 0
                ):
                    cp_data_save.append(cp_csv)

                elif len(data_exist_code_bank) > 0:
                    for ddr in new_ddr:
                        if (
                            ddr["beneficiary_institution"]
                            == cp_csv["beneficiary_institution"]
                            and ddr["counterparty_id_number"]
                            == cp_csv["counterparty_id_number"]
                        ):
                            ddr["id_cp"] = data_exist_code_bank[0]["id"]

            if len(cp_data_save) > 0:
                # -------------- GUARDA COUNTER PARTIES EN COBRE V3 ---------------
                counter_parties_saved = self.cobre_v3_cp.send_all_counterparties(
                    body_counter_party(cp_data_save)
                )

                # --------- COUNTER PARTYS GUARDADOS EN LA BD LOCAL ----------
                self.counterparty.set_counter_party_cobre_body(
                    counter_parties_saved, id_data_load
                )

                # ----------- LE ASIGNA CADA ID CP A CADA DRR ----------------
                for ddr in filter(lambda d: d["id_cp"] == "Pennding", new_ddr):
                    cp = next(
                        (
                            cp_saved
                            for cp_saved in counter_parties_saved
                            if cp_saved["metadata"]["counterparty_id_number"]
                            == ddr["counterparty_id_number"]
                            and cp_saved["metadata"]["beneficiary_institution"]
                            == ddr["beneficiary_institution"]
                        ),
                        None,
                    )
                    ddr["id_cp"] = cp["id"]

            # # --------- ORGANIZA EL PAYLOAD PARA REGISTRAR EL DIRECT DEBIT ----------
            list_data_debit = [[], []]
            for ddr in new_ddr:
                list_data_debit[0].append(
                    {
                        "destination_id": SOURCE_ID,
                        "registration_description": ddr["registration_description"],
                        "destination": {
                            "account_number": ddr["account_number"],
                        },
                    },
                )
                list_data_debit[1].append(
                    ddr["id_cp"]
                )  # ESTE ES EL ID DEL COUNTERPARTY

            # -------- GUARDA LOS DIRECT DEBIT EN COBRE V3 -----------
            direct_debit_saved = self.cobre_v3_ddr.send_all_direct_debit(
                list_data_debit
            )

            logger.debug("PAYLOAD DDR COBRE V3 GUARDADO")

            # -------- GUARDA LOS DIRECT DEBIT EN LA BD LOCAL ---------
            self.debit_register.set_list_debit_registration_cobre_v3(
                compare_ddr(direct_debit_saved, new_ddr)
            )

            return (
                jsonify(
                    {
                        "message": "Archivo procesado exitosamente",
                        "data": direct_debit_saved,
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
            return jsonify({"error": f"Error procesando el archivo: {str(e)}"}), 500

    def export_file_csv_cobre_v3_ddr(self, created_at):
        try:

            # Consulta todos los DDR cargados en {fecha}
            ddr_created_at = self.debit_register.get_debit_register_create_at(
                created_at
            )
            # Convertir la lista de diccionarios a un DataFrame
            df = pd.DataFrame(ddr_created_at)

            # Crear nombre de archivo con fecha/hora para evitar sobrescribir
            filename = f"direct_debit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            # Obtener la ruta absoluta de la carpeta temporal del sistema
            temp_dir = os.path.join(os.path.expanduser("~"), "temp")
            os.makedirs(temp_dir, exist_ok=True)

            file_path = os.path.join(temp_dir, filename)

            # Guardar el DataFrame en un archivo Excel
            df.to_excel(file_path, index=False)

            logger.debug(f"Archivo guardado en: {file_path}")

            return (
                jsonify(
                    {
                        "message": "Archivo guardado exitosamente en la carpeta Temp/",
                        "path": file_path,
                    }
                ),
                200,
            )
        except Exception as e:
            print(f"Error al guardar el archivo Excel: {str(e)}")
            return (
                jsonify({"error": f"Error al guardar el archivo Excel: {str(e)}"}),
                500,
            )


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
