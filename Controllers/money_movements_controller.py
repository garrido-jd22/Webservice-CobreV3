from datetime import datetime
import uuid
from Database.database import Session
import logging
from Models.money_movement import MoneyMovement

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MoneyMovementsController:
    def __init__(self):
        self.session = Session()

    def __del__(self):
        self.session.close()

    def set_money_movement(self, data, extra_string):
        try:
            list_money_movements = []
            count = 0
            for row in data:
                count += 1
                money_movement = MoneyMovement(
                    id=generator_id(count),
                    batch_id=row.get("batch_id", extra_string),
                    external_id=row.get("external_id", ""),
                    typee=row.get("type", "spei"),
                    geo=row.get("geo", ""),
                    source_id=row.get("source_id", ""),
                    destination_id=row.get("destination_id", ""),
                    currency=row.get("currency", "mxn"),
                    amount=row.get("amount", 0.0),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    checker_approval=row.get("checker_approval", False),
                )
                list_money_movements.append(money_movement)

            logger.debug(
                f"Setting money movements with data: {data} y extra_string: {extra_string}"
            )
            # Aquí podrías guardar en la base de datos si es necesario
            # self.session.add_all(list_money_movements)
            # self.session.commit()

            # Construir el payload de respuesta
            payload = [mm.to_dict() for mm in list_money_movements]
            return payload
        except Exception as e:
            logger.error(f"Error setting money movements: {e}")
            return {"error": str(e)}


def generator_id(index):
    prefij = f"mm_00{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
