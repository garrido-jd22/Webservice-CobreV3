from flask import jsonify
from Database.database import Session
import threading
import logging
import uuid
from datetime import datetime

from Models.counter_party import CounterParty as CounterPartyModel
from Controllers.counter_party_controller import CounterParty as CounterPartyController
from Controllers.data_load_controller import DataLoad as DataLoadController
from Controllers.debit_register_controller import (
    DebitRegister as DebitRegisterController,
)

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SOURCE_ID = "acc_1232145215"

class ManagementFileController:

    def __init__(self):
        self.session = Session()
        self.debit_register = DebitRegisterController()

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
                id_cpp = generator_id("cp_00", count)
                counter_party = CounterPartyModel(
                    id=id_cpp,
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
                    # 
                    reference_debit=row["reference_debit"],
                    amount=int(row["amount"]),
                )
                counter_parties.append(counter_party)

            CounterPartyController.set_counter_party(self, counter_parties)

            # Consulta los CounterParties por el ID de carga de datos
            cp_data_load = CounterPartyController.get_counter_party_by_id_load(
                self, id_data_load
            )

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
                        "source_id": SOURCE_ID, # Id del cobrebalance
                        "destination_id": cp["id"],
                        "registration_description": "Subscripción Ejemplo",
                        # BD local
                        "state_local": "01",
                        "state": "PENDING",
                        "code": "PENDING",
                        "description": "PENDING",
                    },
                )

            # Registra los débitos directos en la base de datos en estado PENDING
            DebitRegisterController.set_list_debit_registration(
                self.debit_register, list_data_debit
            )

            # Lanzar temporizador de 24 horas para ejecutar get_debit_register_status
            # 10 SEGUNDOS #
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

    def filter_money_movements(self, id_data_load):
        try:
            # Actualizar el estado de los registros de débito directo
            DebitRegisterController.update_debit_register_status(
                self.debit_register, id_data_load
            )

            # Obtener los registros de débito directo actualizados en formato MONEY MOVEMENT
            DebitRegisterController.get_debit_register_status(
                self.debit_register, id_data_load, "Registered"
            )

            # Aquí podrías llamar a la función para registrar los movimientos de dinero
            logger.debug(
                "Creando movimientos de dinero a partir de los registros de débito directo..."
            )

            return "Registros actualizados"
        except Exception as e:
            logger.error(f"Error setting direct debit registrations: {e}")
            return f"Error: {str(e)}"


def generator_id(test, index):
    prefij = f"{test}{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
