from datetime import datetime
import logging
import uuid
from flask import jsonify
import requests
import time
import random
import string
from Controllers.auth_token_controller import Token as CobreToken
from Controllers.money_movements_controller import MoneyMovementsController
from Models.Money_movement  import DirectDebitMovement
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from pytz import timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from Database.database import Session

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Reducir el nivel de logging de apscheduler y tzlocal
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('tzlocal').setLevel(logging.WARNING)
SOURCE_ID = "acc_znB5gf46CU"


class CobreV3:
    
    BASE_URL = "https://api.cobre.co/v1"
    MESSAGE_ERROR = {"error": "No se pudo obtener el token de autenticación"}
    CONTENT_TYPE = "application/json"

    def __init__(self):
        self.token = CobreToken()
        self.session = requests.Session()
        self.money_movement = MoneyMovementsController()
        #jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
        # Instancia del scheduler con persistencia y zona horaria específica
        self.scheduler = BackgroundScheduler(#jobstores=jobstores, 
                                            imezone=timezone('America/bogota'))
        self.scheduler.start()



    # @staticmethod
    # def send_money_movements(item):
    #     list_items = []
    #     list_items.append(item)
    #     logger.debug(f"items porvenientes del apscheduler = {list_items} \n")
    #     session_local = Session()
    #     try:
    #         # Guardar en la base de datos
    #         logger.info(f"[APScheduler] Ejecutando movimiento de dinero para: {item} \n")
    #         count = 0
    #         money_movement = DirectDebitMovement(
    #             id=generator_id("mm_00", count),
    #             source_id=SOURCE_ID,
    #             destination_id=item["destination_id"],
    #             amount=item["amount"],
    #             date_debit=item["date_debit"],
    #             description=item["metadata"]["description"],
    #             reference_debit=item["metadata"]["reference"],
    #             checker_approval=item["checker_approval"],
    #             hora_fecha_exacta_movimiento=datetime.now(),
    #         )
    #         session_local.add(money_movement)
    #         session_local.commit()
    #         logger.info(f"Movimiento de dinero insertado en la base de datos con id: {money_movement.id}")

    #         # Guardar en historial de jobs ejecutados
    #         # Se importa aquí para evitar problemas de self en staticmethod
    #         from Controllers.cobre_v3_controller import CobreV3
    #         fecha_debit_dt = item["date_debit"]
    #         if isinstance(fecha_debit_dt, str):
    #             try:
    #                 fecha_debit_dt = datetime.strptime(fecha_debit_dt, "%Y-%m-%d")
    #             except Exception:
    #                 pass
    #         CobreV3().guardar_job_ejecutado(item["destination_id"], fecha_debit_dt)

    #     except Exception as e:
    #         session_local.rollback()
    #         logger.error(f"Error al insertar movimiento de dinero: {e}")
    #         return {"error": str(e)}
    #     finally:
    #         session_local.close()
            
            
    def get_cobre_v3_counterparty_by_id_number(self, id_number):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties?counterparty_id_number={id_number}&sensitive_data=true"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            counter_party_content = {
                "counterparty_id_number": id_number,
                "exist": response.json()["contents"],
            }

            return counter_party_content
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def filter_counter_party_id_number(self, lista_counterparties):
        result = []
        with ThreadPoolExecutor(
            max_workers=100
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(
                    self.get_cobre_v3_counterparty_by_id_number,
                    cp["counterparty_id_number"],
                )
                for cp in lista_counterparties
            ]

            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result

    def delete_cobre_v3_counterparty(self, id_counterparty):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties/{id_counterparty}"
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return jsonify({"success": "Counter Party eliminado exitosamente."}), 204
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def set_cobre_v3_counterparty(self, item_counterparty):
        
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties"
            response = self.session.post(
                url, headers=headers, json=item_counterparty, timeout=10
            )
            response.raise_for_status()
            time.sleep(
                0.5
            )  # Espera medio segundo entre cada solicitud para evitar sobrecargar la API
            return response.json()
        except requests.exceptions.HTTPError as e:
            return jsonify({"error": e}), 500
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def send_all_counterparties(self, lista_counterparties):
        result = []
        with ThreadPoolExecutor(
            max_workers=100
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(self.set_cobre_v3_counterparty, cp)
                for cp in lista_counterparties
            ]
            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result
    
    def set_cobre_v3_direct_debit(self, item_direct_debit, counterparty_id):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties/{counterparty_id}/direct_debit_registrations"
            response = self.session.post(
                url, headers=headers, json=item_direct_debit, timeout=10
            )
            response.raise_for_status()
            time.sleep(
                0.5
            )  # Espera medio segundo entre cada solicitud para evitar sobrecargar la API
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.debug("-------------------ERROR-----------------")
            logger.debug("-------------------ERROR-----------------")
            logger.debug(response.json())
            logger.debug("-----------------------------------------")
            logger.debug("-----------------------------------------")
            return jsonify({"error": response.json()}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"error": e}), 500

    def send_all_direct_debit(self, list_debit_id_cp):
        ddr_list, id_cp_list = list_debit_id_cp
        
        result = []
        with ThreadPoolExecutor(
            max_workers=100
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(self.set_cobre_v3_direct_debit, ddr, id_cp)
                for ddr, id_cp in zip(ddr_list, id_cp_list)
            ]

            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result

    @staticmethod
    def send_money_movements(items):
        # required_fields = {"source_id", "destination_id", "amount", "metadata", "checker_approval"}
        # required_metadata = {"description", "reference"}

        # def validate_item(item):
        #     if not all(field in item for field in required_fields):
        #         raise ValueError(f"Faltan campos requeridos en el item: {item}")
        #     if not isinstance(item["metadata"], dict) or not all(m in item["metadata"] for m in required_metadata):
        #         raise ValueError(f"Faltan campos requeridos en metadata: {item}")
        #     return True
        
        logger.debug(f"items porvenientes del apscheduler = {items} \n")

        def process_item(item):
            session_local = Session()
            try:
                
                # Copia el item y elimina date_debit para el request
                item_request = dict(item)
                item_request.pop("date_debit", None)
        
                #validate_item(item)
                token_controller = CobreToken()
                response_token = token_controller.get_token()
                token = response_token.get("token")
                if not token:
                    logger.error("No se pudo obtener el token para enviar el movimiento de dinero a la API de Cobre")
                    return {"error": "No se pudo obtener el token de autenticación"}

                print(f"item_request para enviar a la api= {item_request} \n")
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                url = "https://api.cobre.co/v1/money_movements"
                response = requests.post(url, headers=headers, json=item_request, timeout=10)
                response.raise_for_status()
                response_data = response.json()
                
                logger.info(f"Respuesta de la API de Cobre para movimiento de dinero: {response_data} \n")

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
                logger.info(f"Movimiento de dinero insertado en la base de datos con id: {money_movement.id}")
                return {"success": response_data}
            except requests.exceptions.RequestException as e:
                #logger.error(f"[HTTP ERROR] Error en la petición a la API de Cobre: {e}")
                logger.error(f"mensaje de error: {response.json()}")
                return {"error": f"HTTP error: {str(e)}"}
            except Exception as db_err:
                session_local.rollback()
                logger.error(f"[DB ERROR] Error al insertar movimiento de dinero en la base de datos: {db_err}")
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
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


    #RUTINA PARA VALIDAR LA FECHA EN EL CUAL SE HARÁ LA PROGRAMACIÓN DE EL MOVIMIENTO DE DINERO
    def routine_money_movements(self, payload_list):
        
        print("++++++ Iniciando rutina de movimientos de dinero ++++++ \n")
        #print("### validación de payload_list \n")
        # for item in payload_list:
        #     print(f"Procesando el item: {item} y el id counterparty {item.get('destination_id')}  \n")

        for item in payload_list:
            try:
                fecha_debit = item.get("date_debit")
                print("----------------------------------------------------------------------------------------")
                print(f"Procesando el formato de la fecha inicial dentro de la interacion = {fecha_debit} \n")

                if not fecha_debit:
                    raise ValueError("No se encontró la llave 'date_debit' en el payload \n")

                # Procesamiento y validación de la fecha
                if isinstance(fecha_debit, str):
                    try:
                        fecha_debit_dt = datetime.strptime(fecha_debit, "%Y-%m-%d")
                    except ValueError:
                        raise ValueError("El campo date_debit no tiene un formato válido (YYYY-MM-DD)")
                elif isinstance(fecha_debit, datetime):
                    fecha_debit_dt = fecha_debit
                else:
                    raise ValueError("El campo date_debit no es un string ni un datetime válido")

                now = datetime.now()
                # Si la fecha es hoy, asignar hora/minuto actual +5 minutos
                if fecha_debit_dt.date() == now.date():
                    nueva_hora = (now.hour + ((now.minute + 5) // 60)) % 24
                    nuevo_minuto = (now.minute + 2) % 60
                    fecha_debit_dt = fecha_debit_dt.replace(hour=nueva_hora, minute=nuevo_minuto, second=0)
                else:
                    # Si la fecha no es hoy, asignar 8:00:00
                    fecha_debit_dt = fecha_debit_dt.replace(hour=8, minute=0, second=0)

                print(f"Formato de la Fecha final luego de las validaciones, que usará en el apscheduler = {fecha_debit_dt} \n")

                # Validar que la fecha sea hoy o futura
                # if fecha_debit_dt.date() < now.date():
                #     logger.warning(f"La fecha de ejecución {fecha_debit_dt} ya pasó. No se programará el job para {item.get('destination_id')}")
                #     continue


                # Validar jobs pendientes y ejecutados (historial)
                # jobs = self.scheduler.get_jobs()
                # destination_id = item.get('destination_id')
                # fecha_str = fecha_debit_dt.strftime("%Y-%m-%d %H:%M:%S")

                # # Validar jobs pendientes
                # print(f"Validando si ya existe un job pendiente para destination_id={destination_id} en {fecha_str} \n")
                # for job in jobs:
                #     # Extraer destination_id y fecha de job.id
                #     parts = job.id.split("_")
                #     if len(parts) >= 5:
                #         job_dest_id = parts[3]
                #         # La fecha puede tener espacios, por lo que se une el resto
                #         job_fecha = parts[4]
                #         if len(parts) > 5:
                #             job_fecha += " " + parts[5]
                #         if job_dest_id == str(destination_id) and job_fecha == fecha_str:
                #             logger.error(f"Ya existe un job pendiente para destination_id={destination_id} en {fecha_str}")
                #             print(f"ERROR: Ya existe un job pendiente para destination_id={destination_id} en {fecha_str}")
                #             break
                # print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ \n")
                # print("eliminando jobs anteriores si los hay \n")
                # self.eliminar_jobs_anteriores()
                # generar caracter aleatorio para el job_id
                print(f"Generando job_id para destination_id={item.get('destination_id')} en {item.get('fecha_str')} \n")
                
                random_part = self.random_string(8)
                
                job_id = f"movimiento_id_client_{item.get('destination_id')}{random_part}"
                print(f"job_id generado = {job_id} \n")
                print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ \n")
                try:
                    self.scheduler.add_job(
                        self.__class__.send_money_movements,
                        "date",
                        run_date=fecha_debit_dt,
                        args=[item],
                        id=job_id
                    )
                    
                    logger.debug(f"Tarea programada para {item.get('destination_id')} el {fecha_debit_dt} con job_id {job_id} \n")
                    
                except Exception as sched_err:
                    logger.warning(f"Error al programar la tarea para {item.get('destination_id')}: {sched_err} \n")
            except ValueError as ve:
                logger.error(f"Error de formato de fecha para {item.get('destination_id')}: {ve}")
            except Exception as e:
                logger.error(f"Error general al procesar el item {item.get('destination_id')}: {e}")

        # Imprimir los jobs futuros o pendientes
        # print("\n==== Jobs pendientes o futuros en APScheduler ====")
        # jobs = self.scheduler.get_jobs()
        # if not jobs:
        #     logger.info("No hay jobs pendientes o futuros.")
        # else:
        #     for job in jobs:
        #         logger.info(f"ID: {job.id} | Próxima ejecución: {job.next_run_time} \n")
        #         print("--------------------------------------------------------------------")
                #print(f"ID: {job.id} | Próxima ejecución: {job.next_run_time}")



    # def eliminar_jobs_anteriores(self):
    #     print("++++++ Iniciando eliminación de jobs anteriores ++++++ \n")
    #     #now = datetime.now(self.scheduler.timezone)
    #     now =  datetime.now()
    #     jobs = self.scheduler.get_jobs()
    #     for job in jobs:
    #         print(f"Verificando job: {job.id} con próxima ejecución: {job.next_run_time} \n")
    #         if job.next_run_time < now:
    #             try:
    #                 self.scheduler.remove_job(job.id)
    #                 logger.info(f"Job {job.id} eliminado por ser anterior a la fecha actual.")
    #             except LookupError:
    #                 logger.warning(f"No se pudo eliminar el job {job.id} (puede que ya haya sido ejecutado/eliminado).")
                
def generator_id(test, index):
    prefij = f"{test}{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned



