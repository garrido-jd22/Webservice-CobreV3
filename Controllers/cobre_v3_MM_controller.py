from datetime import datetime
import logging
import uuid
from flask import jsonify
import requests
import random
import string
from Controllers.auth_token_controller import Token as CobreToken
from Controllers.money_movements_controller import MoneyMovementsController
from Models.Money_movement import DirectDebitMovement
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from Database.database import Session

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Reducir el nivel de logging de apscheduler y tzlocal
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("tzlocal").setLevel(logging.WARNING)
SOURCE_ID = "acc_znB5gf46CU"


class CobreV3MoneyMovement:

    BASE_URL = "https://api.cobre.co/v1"
    MESSAGE_ERROR = {"error": "No se pudo obtener el token de autenticación"}
    CONTENT_TYPE = "application/json"

    def __init__(self):
        self.token = CobreToken()
        self.session = requests.Session()
        self.money_movement = MoneyMovementsController()
        # jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
        # Instancia del scheduler con persistencia y zona horaria específica
        self.scheduler = BackgroundScheduler(  # jobstores=jobstores,
            imezone=timezone("America/bogota")
        )
        self.scheduler.start()

    @staticmethod
    def send_money_movements(items):

        logger.debug(f"items porvenientes del apscheduler = {items} \n")

        def process_item(item):
            session_local = Session()
            try:

                # Copia el item y elimina date_debit para el request
                item_request = dict(item)
                item_request.pop("date_debit", None)

                # validate_item(item)
                token_controller = CobreToken()
                response_token = token_controller.get_token()
                token = response_token.get("token")
                if not token:
                    logger.error(
                        "No se pudo obtener el token para enviar el movimiento de dinero a la API de Cobre"
                    )
                    return {"error": "No se pudo obtener el token de autenticación"}

                print(f"item_request para enviar a la api= {item_request} \n")
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }

                url = "https://api.cobre.co/v1/money_movements"
                response = requests.post(
                    url, headers=headers, json=item_request, timeout=10
                )
                response.raise_for_status()
                response_data = response.json()

                logger.info(
                    f"Respuesta de la API de Cobre para movimiento de dinero: {response_data} \n"
                )

                # Usar el id retornado por la API
                api_id = response_data.get("id")
                if not api_id:
                    raise ValueError("La respuesta de la API no contiene 'id'")

                money_movement = DirectDebitMovement(
                    id=api_id,
                    source_id=item["source_id"],
                    destination_id=item["destination_id"],
                    amount=item["amount"],
                    date_debit=item.get("date_debit"),
                    description=item["metadata"]["description"],
                    reference_debit=item["metadata"]["reference"],
                    checker_approval=item["checker_approval"],
                    hora_fecha_exacta_movimiento=datetime.now(),
                )
                session_local.add(money_movement)
                session_local.commit()
                logger.info(
                    f"Movimiento de dinero insertado en la base de datos con id: {money_movement.id}"
                )
                return {"success": response_data}
            except requests.exceptions.RequestException as e:
                # logger.error(f"[HTTP ERROR] Error en la petición a la API de Cobre: {e}")
                logger.error(f"mensaje de error: {response.json()}")
                return {"error": f"HTTP error: {str(e)}"}
            except Exception as db_err:
                session_local.rollback()
                logger.error(
                    f"[DB ERROR] Error al insertar movimiento de dinero en la base de datos: {db_err}"
                )
                return {"error": f"DB error: {str(db_err)}"}
            finally:
                session_local.close()

        # Si recibe un solo dict, lo convierte en lista
        if isinstance(items, dict):
            items = [items]

        results = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(process_item, item) for item in items]
            for future in as_completed(futures):
                results.append(future.result())
        return results

    @staticmethod
    def random_string(length=6):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    # RUTINA PARA VALIDAR LA FECHA EN EL CUAL SE HARÁ LA PROGRAMACIÓN DE EL MOVIMIENTO DE DINERO
    def routine_money_movements(self, payload_list):

        print("++++++ Iniciando rutina de movimientos de dinero ++++++ \n")

        for item in payload_list:
            try:
                fecha_debit = item.get("date_debit")
                print(
                    "----------------------------------------------------------------------------------------"
                )
                print(
                    f"Procesando el formato de la fecha inicial dentro de la interacion = {fecha_debit} \n"
                )

                if not fecha_debit:
                    raise ValueError(
                        "No se encontró la llave 'date_debit' en el payload \n"
                    )

                # Procesamiento y validación de la fecha
                if isinstance(fecha_debit, str):
                    try:
                        fecha_debit_dt = datetime.strptime(fecha_debit, "%Y-%m-%d")
                    except ValueError:
                        raise ValueError(
                            "El campo date_debit no tiene un formato válido (YYYY-MM-DD)"
                        )
                elif isinstance(fecha_debit, datetime):
                    fecha_debit_dt = fecha_debit
                else:
                    raise ValueError(
                        "El campo date_debit no es un string ni un datetime válido"
                    )

                now = datetime.now()
                # Si la fecha es hoy, asignar hora/minuto actual +5 minutos
                if fecha_debit_dt.date() == now.date():
                    nueva_hora = (now.hour + ((now.minute + 5) // 60)) % 24
                    nuevo_minuto = (now.minute + 2) % 60
                    fecha_debit_dt = fecha_debit_dt.replace(
                        hour=nueva_hora, minute=nuevo_minuto, second=0
                    )
                else:
                    # Si la fecha no es hoy, asignar 8:00:00
                    fecha_debit_dt = fecha_debit_dt.replace(hour=8, minute=0, second=0)

                print(
                    f"Formato de la Fecha final luego de las validaciones, que usará en el apscheduler = {fecha_debit_dt} \n"
                )

                print(
                    f"Generando job_id para destination_id={item.get('destination_id')} en {item.get('fecha_str')} \n"
                )

                random_part = self.random_string(8)

                job_id = (
                    f"movimiento_id_client_{item.get('destination_id')}{random_part}"
                )
                print(f"job_id generado = {job_id} \n")
                print(
                    "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ \n"
                )
                try:
                    self.scheduler.add_job(
                        self.__class__.send_money_movements,
                        "date",
                        run_date=fecha_debit_dt,
                        args=[item],
                        id=job_id,
                    )

                    logger.debug(
                        f"Tarea programada para {item.get('destination_id')} el {fecha_debit_dt} con job_id {job_id} \n"
                    )

                except Exception as sched_err:
                    logger.warning(
                        f"Error al programar la tarea para {item.get('destination_id')}: {sched_err} \n"
                    )
            except ValueError as ve:
                logger.error(
                    f"Error de formato de fecha para {item.get('destination_id')}: {ve}"
                )
            except Exception as e:
                logger.error(
                    f"Error general al procesar el item {item.get('destination_id')}: {e}"
                )


def generator_id(test, index):
    prefij = f"{test}{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned
