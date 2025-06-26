from datetime import datetime
import uuid

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
                    CobreBalanceModel.id == DirectDebitRegistrationModel.destination_id,
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
                    .filter(
                        CobreAviableServicesModel.fk_cobre_balance == ddr.destination_id
                    )
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
                destination_id=data["destination_id"],  # Id Cobre Balance
                registration_description=data["registration_description"],
                fk_counterparty=counterparty_id,  # Id del counterparty
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
                f"Setting direct debit registrations for counterparty {counterparty_id} with data: {data}"
            )
            return jsonify({"message": "datos ingresados en la tabla correctamente."})
        except Exception as e:
            logger.error(f"Error setting direct debit registrations: {e}")
            return jsonify({"error": f"Error: {str(e)}"}), 500


def generator_id(text):
    prefij = text
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
