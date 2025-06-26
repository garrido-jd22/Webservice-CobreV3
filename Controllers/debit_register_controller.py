from datetime import datetime
import uuid
from Database.database import Session
import logging

from Models.direct_debit_registration import (
    DirectDebitRegistration as DirectDebitRegistrationModel,
)

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DebitRegister:

    def __init__(self):
        self.session = Session()

    def __del__(self):
        self.session.close()

    def set_direct_debit_registrations(self, counterparty_id, data):

        try:
            # Aquí se implementaría la lógica para registrar el débito directo

            list_debit_register = []
            count = 0
            for row in data:
                count += 1
                debit_register = DirectDebitRegistrationModel(
                    id=generator_id(count),
                    destination_id=row["destination_id"],
                    registration_description=row["registration_description"],
                    state=row["state"],
                    code=row["code"],
                    description=row["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                list_debit_register.append(debit_register)

            # Por ejemplo, crear un nuevo registro en la base de datos
            logger.debug(
                f"Setting direct debit registrations for counterparty {counterparty_id} with data: {data}"
            )
            # Simulación de éxito
            return True
        except Exception as e:
            logger.error(f"Error setting direct debit registrations: {e}")
            return False


def generator_id(index):
    prefij = f"ddr_00{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
