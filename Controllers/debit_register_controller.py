from datetime import datetime
import uuid
import threading

from flask import jsonify
from Database.database import Session
import logging

from Models.direct_debit_registration import (
    DirectDebitRegistration as DirectDebitRegistrationModel,
)
from Models.cobre_balance import (
    CobreBalance as CobreBalanceModel,
)
from Models.cobre_balance import CobreAvailableServices as CobreAviableServicesModel
from Models.counter_party import CounterParty as CounterPartyModel


# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DebitRegister:

    def __init__(self):
        self.session = Session()

    def __del__(self):
        self.session.close()

    def get_all_direct_debit_registrations(self):
        try:
            # Obtener todos los registros de DirectDebitRegistration
            debit_registers = (
                self.session.query(DirectDebitRegistrationModel, CobreBalanceModel)
                .join(
                    CobreBalanceModel,
                    CobreBalanceModel.id == DirectDebitRegistrationModel.source_id,
                )
                .all()
            )
            logger.debug(
                "Consultando informacion del Cobre balance e iterando registros..."
            )

            list_debit_registers = []

            for ddr, acc in debit_registers:
                # Obtener los servicios disponibles para el balance de Cobre
                cobre_aviable_service = (
                    self.session.query(CobreAviableServicesModel)
                    .filter(CobreAviableServicesModel.fk_cobre_balance == ddr.source_id)
                    .all()
                )
                list_aviable_service = []
                for acc_info in cobre_aviable_service:
                    list_aviable_service.append(acc_info.service_name)

                list_debit_registers.append(
                    {
                        "id": ddr.id,
                        "destination_id": ddr.destination_id,
                        "destination": {
                            "alias": acc.alias,
                            "provider_id": acc.provider_id,
                            "provider_name": acc.provider_name,
                            "account_number": acc.account_number,
                            "metadata": {
                                "cobre_tag": "@example0015",
                                "available_services": list_aviable_service,
                            },
                            "account_type": acc.account_type,
                        },
                        "state_local": ddr.state_local,
                        "status": {
                            "state": ddr.state,
                            "code": ddr.code,
                            "description": ddr.description,
                        },
                        "registration_description": ddr.registration_description,
                        "created_at": ddr.created_at,
                        "updated_at": ddr.updated_at,
                    }
                )

            return jsonify(list_debit_registers), 200

        except Exception as e:
            logger.error(f"Error retrieving direct debit registrations: {e}")
            return jsonify({"error": f"Error retrieving data: {str(e)}"}), 500

    def set_direct_debit_registrations(self, counterparty_id, data):
        try:
            debit_register = DirectDebitRegistrationModel(
                id=generator_id("ddr_00"),
                destination_id=counterparty_id,  # Id Cobre Balance
                registration_description=data["registration_description"],
                source_id=data["source_id"],  # Id del cobrebalance
                # Estos campos miden el estado del registro en la BD local
                state_local=data["state_local"],
                # Estos campos miden el estado del registro
                state=data["state"],
                code=data["code"],
                description=data["description"],
                # Campos de fecha
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            self.session.add(debit_register)
            self.session.commit()
            logger.debug(
                f"Registro de los debitos insertados coccrectamente  {counterparty_id} with data: {data}"
            )

            logger.debug("activando temporizador...")
            # Lanzar temporizador de 24 horas para ejecutar get_debit_register_status

            # 30 SEGUNDOS ##

            timer = threading.Timer(30, self.get_debit_register_status)
            timer.daemon = True
            timer.start()
            print("temporizador activado")

            return jsonify({"message": "datos ingresados en la tabla correctamente.\n"})
        except Exception as e:
            logger.error(f"Error setting direct debit registrations: {e}")
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def set_list_debit_registration(self, data_list):
        try:
            debit_register = []
            for ddr in data_list:
                debit_register.append(
                    DirectDebitRegistrationModel(
                        id=generator_id("ddr_00"),
                        destination_id=ddr["destination_id"],  # Id del Cobre balance
                        registration_description=ddr["registration_description"],
                        fk_id_counterparty=ddr[
                            "fk_id_counterparty"
                        ],  # Id del counterparty
                        # Estos campos miden el estado del registro en la BD local
                        state_local=ddr["state_local"],
                        # Estos campos miden el estado del registro
                        state=ddr["state"],
                        code=ddr["code"],
                        description=ddr["description"],
                        # Campos de fecha
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                )
            self.session.add_all(debit_register)
            self.session.commit()
            logger.debug(
                f"Registro de los debitos insertados correctamente with data: {data_list}"
            )

            return jsonify({"message": "datos ingresados en la tabla correctamente.\n"})
        except Exception as e:
            logger.error(f"Error setting direct debit registrations: {e}")
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def set_list_debit_registration_cobre_v3(self, data_list):
        try:
            debit_register = []
            for ddr in data_list:
                debit_register.append(
                    DirectDebitRegistrationModel(
                        id=ddr["id"],
                        destination_id=ddr["destination_id"],  # Id del Cobre balance
                        registration_description=ddr["registration_description"],
                        fk_id_counterparty=ddr[
                            "fk_id_counterparty"
                        ],  # Id del counterparty
                        fk_data_load=ddr[
                            "fk_data_load"
                        ],  # Id del counterparty
                        # Estos campos miden el estado del registro en la BD local
                        state_local=ddr["state_local"],
                        # Estos campos miden el estado del registro
                        state=ddr["state"],
                        code=ddr["code"],
                        description=ddr["description"],
                        # Campos de fecha
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        # 
                        reference=ddr["reference"],
                        amount=ddr["amount"],
                        date_debit=ddr["date_debit"],
                    )
                )
            self.session.add_all(debit_register)
            self.session.commit()
            logger.debug(
                f"Registro de los debitos insertados correctamente with data: {data_list}"
            )

            return jsonify({"message": "datos ingresados en la tabla correctamente.\n"})
        except Exception as e:
            logger.error(f"Error setting direct debit registrations: {e}")
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def update_debit_register_status(self, id_load):
        try:
            debit_register = (
                self.session.query(DirectDebitRegistrationModel, CounterPartyModel)
                .join(
                    CounterPartyModel,
                    CounterPartyModel.id
                    == DirectDebitRegistrationModel.fk_id_counterparty,
                )
                .filter(
                    CounterPartyModel.fk_data_load == id_load,
                    DirectDebitRegistrationModel.state == "processing",
                )
                .all()
            )
            logger.debug(
                f"Consultando informacion del Cobre balance e iterando registros para el id de carga: {id_load}"
            )
            for ddr, cp in debit_register:
                ddr.state_local = "02"
                ddr.state = "Registered"
                ddr.code = "RD000"
                ddr.description = "NA"

            self.session.commit()
            return f"{len(debit_register)} registros actualizados"

        except Exception as e:
            logger.error(f"Error setting direct debit registrations: {e}")
            return f"Error: {str(e)}"

    def get_debit_register_status(self, id_load, state):
        try:
            debit_register = (
                self.session.query(DirectDebitRegistrationModel, CounterPartyModel)
                .join(
                    CounterPartyModel,
                    CounterPartyModel.id
                    == DirectDebitRegistrationModel.fk_id_counterparty,
                )
                .filter(
                    CounterPartyModel.fk_data_load == id_load,
                    DirectDebitRegistrationModel.state == state,
                )
                .all()
            )

            payload = []
            for ddr, cp in debit_register:
                payload.append(
                    {
                        "source_id": ddr.destination_id,
                        "destination_id": ddr.fk_id_counterparty,  # direct_debit_registration.destination_id <--- AQUI VA EL ID DEL COUNTER PARTY
                        "amount": cp.amount,  # counterparty.amount
                        "date_debit": cp.date_debit,  # counterparty.date_debit
                        "metadata": {
                            "description": ddr.registration_description,  # direct_debit_registration.registration_description
                            "reference": cp.reference,  # counterparty.reference
                        },
                        "checker_approval": False,
                    }
                )
            print(
                "payload del get a la base de datos de directdebit por estado",
                payload,
            )
            return payload
        except Exception as e:
            logger.error(f"Error en get_debit_register_status: {e}")
            return []


def generator_id(text):
    prefij = text
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
