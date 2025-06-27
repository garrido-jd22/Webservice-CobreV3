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

# from Controllers.money_movements_controller import MoneyMovementsController


class ManagementFileController:

    def __init__(self):
        self.session = Session()

    def __del__(self):
        self.session.close()

    # funcion leer archivo cvs
    def read_file_csv(self, data_csv):
        try:
            counter_parties = []

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
            list_data_debit = []
            for cp in cp_data_load[0].get_json():
                list_data_debit.append(
                    {
                        "id_counterparty": cp["id"],
                        "destination_id": "acc_0011223344",
                        "registration_description": "Subscripción Ejemplo",
                        # BD local
                        "state_local": "01",
                        "state": "PENDING",
                        "code": "PENDING",
                        "description": "PENDING",
                    },
                )
            DebitRegisterController.set_list_debit_registration(self, list_data_debit)
            debit_result = DebitRegisterController().get_debit_register_status(
                self, data_csv
            )

            # Money Movement
            # Primero consultar de debit register todos los Debitos Directos por el ID de carga de datos y por el estado RD000 o Registered.
            # print("payload obtenido por estado y por id del  debit register", Results)
            # Guardar los movimientos de dinero en la base de datos.
            # money_movement_controller = MoneyMovementsController()
            # Se asume que el estado es el mismo para todos los registros, se toma del primer elemento si existe
            # estado = Results[0]["esatdoFinalRegisterDebit"] if Results else None
            # money_movements_payload = money_movement_controller.set_money_movement(
            #     Results, estado
            # )
            # print(
            #     "payload generado por money_movement_controller:",
            #     money_movements_payload,
            # )

            return (
                jsonify(
                    {
                        "message": "Archivo procesado exitosamente",
                        "data": cp_data_load[0].get_json(),
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


def generator_id(test, index):
    prefij = f"{test}{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
