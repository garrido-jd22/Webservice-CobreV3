from flask import jsonify
from Database.database import Session

import csv
import uuid
from datetime import datetime

from Models.counter_party import CounterParty as CounterPartyModel
from Controllers.counter_party_controller import CounterParty as CounterPartyController
from Controllers.data_load_controller import DataLoad as DataLoadController
from Controllers.debit_register_controller import (
    DebitRegister as DebitRegisterController,
)


class ManagementFileController:

    def __init__(self):
        self.session = Session()

    def __del__(self):
        self.session.close()

    # funcion leer archivo c.vs
    def read_file_csv(self, file_path):
        try:
            counter_parties = []
            # Abre el archivo CSV en modo lectura
            with open(
                file_path, mode="r", newline="", encoding="utf-8-sig"
            ) as archivo_csv:

                # Usa csv.DictReader para leer el archivo como diccionarios (cada fila es un diccionario)
                lector_csv = csv.DictReader(archivo_csv)
                # Convertir DictReader a lista de diccionarios
                data_csv = list(lector_csv)

                # Generar un ID único para la carga de datos
                id_data_load = generator_id("load_00", 1)

                # Registrar la carga de datos en la base de datos
                DataLoadController.set_data_load(self, id_data_load, "PENDING")

                counter_parties = []
                count = 0

                for row in data_csv:
                    count += 1
                    counter_party = CounterPartyModel(
                        id=generator_id("cp_00", count),
                        fk_data_load=id_data_load,
                        geo=row["geo"],
                        type=row["type"],
                        alias=row["alias"],
                        beneficiary_institution=row["beneficiary_institution"],
                        account_number=int(row["account_number"]),
                        counterparty_fullname=row["counterparty_fullname"],
                        counterparty_id_type=row["counterparty_id_type"],
                        counterparty_id_number=int(row["account_number"]),
                        counterparty_phone=int(row["counterparty_phone"]),
                        counterparty_email=row["counterparty_email"],
                        fecha_reg=datetime.now(),
                    )
                    counter_parties.append(counter_party)

                CounterPartyController.set_counter_party(self, counter_parties)

                # Consulta los CounterParties por el ID de carga de datos
                cp_data_load = CounterPartyController.get_counter_party_by_id_load(
                    self, id_data_load
                )

                # Itera sobre los CounterParties obtenidos y registra los débitos directos
                for cp in cp_data_load[0].get_json():
                    DebitRegisterController.set_direct_debit_registrations(
                        self,
                        cp["id"],
                        {
                            "destination_id": "acc_0011223344",
                            "registration_description": "Subscripción Ejemplo",
                            "state": "Registered",
                            "code": "RD000",
                            "description": "NA",
                        },
                    )

            return (
                jsonify(
                    {
                        "message": "Archivo procesado exitosamente",
                        "data": data_csv,
                    }
                ),
                200,
            )

        except FileNotFoundError:
            return (
                jsonify({"error": f"El archivo '{file_path}' no fue encontrado."}),
                404,
            )
        except Exception as e:
            return jsonify({"error": f"Error procesando el archivo: {str(e)}"}), 500


def generator_id(test, index):
    prefij = f"{test}{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
