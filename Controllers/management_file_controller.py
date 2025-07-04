import threading
from flask import jsonify
from Database.database import Session
import logging
import uuid
from datetime import datetime

from Models.counter_party import CounterParty as CounterPartyModel
from Controllers.counter_party_controller import CounterParty as CounterPartyController
from Controllers.data_load_controller import DataLoad as DataLoadController
from Controllers.debit_register_controller import (
    DebitRegister as DebitRegisterController,
)

# Cobre V3
from Controllers.cobre_v3_controller import CobreV3 as CobreV3Controller

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SOURCE_ID = "acc_znB5gf46CU"


class ManagementFileController:

    def __init__(self):
        self.session = Session()
        self.cobre_v3 = CobreV3Controller()
        self.counterparty = CounterPartyController()
        self.debit_register = DebitRegisterController()
        self.data_load = DataLoadController()

    def __del__(self):
        self.session.close()

    # funcion leer archivo cvs
    def read_file_csv(self, data_csv):
        try:
            counter_parties = []

            # Generar un ID único para la carga de datos
            id_data_load = generator_id("load_00", 1)

            # Registrar la carga de datos en la base de datos
            self.data_load.set_data_load(self, id_data_load, "PENDING")

            counter_parties = []
            count = 0

            for row in data_csv:
                count += 1
                id_cpp = generator_id("cp_00", count)
                counter_parties.append(
                    {
                        "id": id_cpp,
                        "fk_data_load": id_data_load,
                        "geo": row["geo"],
                        "type": row["type"],
                        "alias": row["alias"],
                        "beneficiary_institution": row["beneficiary_institution"],
                        "account_number": int(row["account_number"]),
                        "counterparty_fullname": row["counterparty_fullname"],
                        "counterparty_id_type": row["counterparty_id_type"],
                        "counterparty_id_number": int(row["counterparty_id_number"]),
                        "counterparty_phone": row["counterparty_phone"],
                        "counterparty_email": row["counterparty_email"],
                        "fecha_reg": datetime.now(),
                        "reference_debit": row["reference_debit"],
                        "amount": int(row["amount"]),
                    }
                )

            self.counterparty.set_counter_party(counter_parties, id_data_load)

            # Consulta los CounterParties por el ID de carga de datos
            cp_data_load = self.counterparty.get_counter_party_by_id_load(id_data_load)

            print(
                "datos Retornados por el metodo get a la bse de datos por id de carga = \n",
                cp_data_load[0].get_json(),
                "\n",
            )

            # Itera sobre los CounterParties obtenidos y registra los débitos directos
            list_data_debit = []
            for cp in cp_data_load[0].get_json():
                list_data_debit.append(
                    {
                        "destination_id": SOURCE_ID,
                        "registration_description": "Subscripción Ejemplo",
                        # BD local
                        "fk_id_counterparty": cp["id"],  # Id del counter party
                        "state_local": "01",
                        "state": "PENDING",
                        "code": "PENDING",
                        "description": "PENDING",
                    },
                )

            # Registra los débitos directos en la base de datos en estado PENDING
            self.debit_register.set_list_debit_registration(list_data_debit)

            # Lanzar temporizador de 24 horas para ejecutar get_debit_register_status
            # 86.400 SEGUNDOS #
            logger.debug("activando temporizador...")

            timer = threading.Timer(
                10,
                self.filter_money_movements,
                args=(id_data_load,),
            )  # con coma final para que sea una tupla de un solo elemento
            timer.daemon = True
            timer.start()

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

    def read_file_csv_cobre_v3(self, data_csv):
        try:
            counter_parties = []

            # Generar un ID único para la carga de datos
            id_data_load = generator_id("load_00", 1)

            # Registrar la carga de datos en la base de datos
            self.data_load.set_data_load(id_data_load, "PENDING")

            # Preparar los datos de los CounterParties
            counter_parties = []
            for row in data_csv:
                counter_parties.append(
                    {
                        "geo": row["geo"],
                        "type": row["type"],
                        "alias": row["alias"],
                        "metadata": {
                            "account_number": int(row["account_number"]),
                            "counterparty_fullname": row["counterparty_fullname"],
                            "counterparty_id_type": row["counterparty_id_type"],
                            "counterparty_id_number": int(
                                row["counterparty_id_number"]
                            ),
                            "counterparty_phone": row["counterparty_phone"],
                            "counterparty_email": row["counterparty_email"],
                            "beneficiary_institution": row["beneficiary_institution"],
                        },
                    }
                )

            print("Datos Counter Party COBRE V3: \n", counter_parties)

            # Guardar los datos de los CounterParties en COBRE V3
            counter_parties_saved = self.cobre_v3.send_all_counterparties(
                counter_parties
            )

            # Compara con la lista de Counterparties para guardar el amount y referencia
            for cp_saved in counter_parties_saved:
                for cp_new_load in data_csv:
                    if (
                        int(cp_new_load["counterparty_id_number"])
                        == cp_saved["metadata"]["counterparty_id_number"]
                    ):
                        cp_saved["metadata"]["reference_debit"] = cp_new_load[
                            "reference_debit"
                        ]
                        cp_saved["metadata"]["amount"] = int(cp_new_load["amount"])
                        break

            # --------- Guardar los datos de los CounterParties en LOCAL WEB SERVICE ----------
            self.counterparty.set_counter_party_cobre_body(
                counter_parties_saved, id_data_load
            )

            # Itera sobre los CounterParties obtenidos y registra los débitos directos
            list_data_debit = [[], []]
            for cp in counter_parties_saved:
                list_data_debit[0].append(
                    {
                        "destination_id": SOURCE_ID,
                        "registration_description": "Subscripción Ejemplo",
                    },
                )
                list_data_debit[1].append(cp["id"])

            # Registra los débitos directos en la base de datos en estado PENDING
            # Guardar los datos de los DIRECT DEBIT en COBRE V3
            direct_debit_saved = self.cobre_v3.send_all_direct_debit(list_data_debit)

            return (
                jsonify(
                    {
                        "message": "Archivo procesado exitosamente",
                        "data": counter_parties_saved,
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

    def filter_money_movements(self, id_data_load):
        try:
            # Actualizar el estado de los registros de débito directo
            self.debit_register.update_debit_register_status(id_data_load)

            # Obtener los registros de débito directo actualizados en formato MONEY MOVEMENT
            data_payload_Register = self.debit_register.get_debit_register_status(
                id_data_load, "Registered"
            )

            print(
                "registros de débito directo actualizados en formato MONEY MOVEMENT: \n",
                data_payload_Register,
            )

            # Llamar a la rutina de movimientos de dinero
            self.routine_money_movements(data_payload_Register)

            logger.debug(
                "Creando movimientos de dinero a partir de los registros de débito directo..."
            )

            return data_payload_Register
        except Exception as e:
            logger.error(f"Error setting direct debit registrations: {e}")
            return f"Error: {str(e)}"

    def routine_money_movements(self, data_payload_Register):
        from Controllers.money_movements_controller import MoneyMovementsController

        money_movement_controller = MoneyMovementsController()
        money_movement_controller.routine_money_movements(data_payload_Register)


def generator_id(test, index):
    prefij = f"{test}{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
