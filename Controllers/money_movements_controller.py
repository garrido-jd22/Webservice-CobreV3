from datetime import datetime
import uuid
from Database.database import Session
import logging
from Models.money_movement import MoneyMovement
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MoneyMovementsController:
    def __init__(self):
        self.session = Session()
        # Configuración del JobStore para persistencia en SQLite
        jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
        # Instancia del scheduler con persistencia
        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        self.scheduler.start()

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

    def routine_money_movements(self, payload_list):
        try:
            money_movement_to_save = (
                []
            )  # Lista para guardar los movimientos a persistir
            for item in payload_list:
                # Validar que el status sea 'registered'
                status = item.get("status")
                if status != "registered":
                    raise Exception(
                        f"El status del registro no es 'registered': {status}"
                    )
                fecha_debit = item.get("fecha_debit")
                if not fecha_debit:
                    raise Exception(
                        "No se encontró la llave 'fecha_debit' en el payload"
                    )
                # Convertir la fecha_debit a objeto datetime
                fecha_debit_dt = datetime.strptime(fecha_debit, "%Y-%m-%d")
                # Programar la ejecución del movimiento de dinero usando APScheduler
                self.scheduler.add_job(
                    self.ejecutar_movimiento,
                    "date",
                    run_date=fecha_debit_dt,
                    args=[item],
                    id=f"movimiento_{item.get('reference_debit', '')}_{fecha_debit}",
                    replace_existing=True,
                )
                logger.debug(
                    f"Tarea programada para {item.get('reference_debit', '')} el {fecha_debit_dt}"
                )
                # Agregar el movimiento a la lista para guardar, con el nuevo estatus
                movimiento = item.copy()
                movimiento["estatus_money_movement"] = "initiated"
                money_movement_to_save.append(movimiento)
            # Guardar los movimientos en la base de datos usando un nuevo método
            self.save_money_movements(money_movement_to_save)
        except Exception as e:
            logger.error(f"Error en routine_money_movements: {e}")
            raise

    def ejecutar_movimiento(self, payload):
        # Aquí va la lógica que se ejecutará en la fecha programada
        logger.info(f"Ejecutando movimiento de dinero para: {payload}")
        # Aquí podrías actualizar el estatus en la base de datos, enviar notificaciones, etc.

    def save_money_movements(self, movimientos):
        # Método para guardar los movimientos en la base de datos
        try:
            # Aquí deberías transformar cada dict en una instancia de tu modelo MoneyMovement
            # y guardarlos en la base de datos. Ejemplo:
            # list_money_movements = [MoneyMovement(**mov) for mov in movimientos]
            # self.session.add_all(list_money_movements)
            # self.session.commit()
            logger.info(f"Movimientos guardados en la base de datos: {movimientos}")
        except Exception as e:
            logger.error(f"Error guardando movimientos: {e}")
            raise


def generator_id(index):
    prefij = f"mm_00{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
