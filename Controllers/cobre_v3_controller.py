from datetime import datetime
import logging
import uuid
from flask import jsonify
import requests
import time
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
        jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
        # Instancia del scheduler con persistencia y zona horaria específica
        self.scheduler = BackgroundScheduler(jobstores=jobstores, timezone=timezone('America/bogota'))
        self.scheduler.start()

    def get_cobre_v3_balance(self):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/accounts"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def get_cobre_v3_counterparty(self):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties?sensitive_data=true"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

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


    # Método estático para enviar movimientos de dinero
    @staticmethod
    def send_money_movements(item):
        
        list_items = []
        
        list_items.append(item)
        
        logger.debug(f"items porvenientes del apscheduler = {list_items} \n")
        
        session_local = Session()
        try:
            # Guardar en la base de datos
            logger.info(f"[APScheduler] Ejecutando movimiento de dinero para: {item} \n")
            count = 0
            money_movement = DirectDebitMovement(
                id=generator_id("mm_00", count),
                source_id=SOURCE_ID,
                destination_id=item["destination_id"],
                amount=item["amount"],
                date_debit=item["date_debit"],
                description=item["metadata"]["description"],
                reference_debit=item["metadata"]["reference"],
                checker_approval=item["checker_approval"],
                hora_fecha_exacta_movimiento=datetime.now(),
            )
            session_local.add(money_movement)
            session_local.commit()
            logger.info(f"Movimiento de dinero insertado en la base de datos con id: {money_movement.id}")

            # Enviar el item a la API de Cobre
            # Obtener el token usando el controlador
            # token_controller = CobreToken()
            # response_token = token_controller.get_token()
            # token = response_token.get("token")
            # if not token:
            #     logger.error("No se pudo obtener el token para enviar el movimiento de dinero a la API de Cobre")
            #     return {"error": "No se pudo obtener el token de autenticación"}

            # headers = {
            #     "Authorization": f"Bearer {token}",
            #     "Content-Type": "application/json",
            # }
            # url = f"https://api.cobre.co/v1/money_movements"  # Ajusta el endpoint si es diferente
            # try:
            #     response = requests.post(url, headers=headers, json=item, timeout=10)
            #     response.raise_for_status()
                
                
            #     logger.info(f"Respuesta de la API de Cobre para movimiento de dinero: {response.json()}")
            #     return {"success": response.json()}
            # except requests.exceptions.RequestException as e:
            #     logger.error(f"Error al enviar el movimiento de dinero a la API de Cobre: {e}")
            #     return {"error": str(e)}
        except Exception as e:
            session_local.rollback()
            logger.error(f"Error al insertar movimiento de dinero: {e}")
            return {"error": str(e)}
        finally:
            session_local.close()
        
        
        
        
        
        
        
        
        
    #RUTINA PARA EL ENVÍO DE MOVIMIENTOS DE DINERO
    def routine_money_movements(self, payload_list):
        
        print("++++++ Iniciando rutina de movimientos de dinero ++++++ \n")
        # print("### validación de payload_list \n")
        # for item in payload_list:
        #     #recorrer payload_list
        #     print(f"Procesando el item: {item} y el id counterparty {item.get("destination_id")}  \n")
        
        for item in payload_list:
            
            fecha_debit = item.get("date_debit")
            
            
            print(f"Procesando el formato de la fecha inicial dentro de la interacion = {fecha_debit} \n")
            
            if not fecha_debit:
                raise Exception("No se encontró la llave 'date_debit' en el payload \n")
            # Si la fecha viene como string con formato completo, puedes modificar la hora aquí
            if isinstance(fecha_debit, str):
                # Cambia aquí la hora que quieras probar
                hora_prueba = "11:38:00"  # <-- Cambiar esto para pruebas
                
                # Si el string ya tiene formato 'YYYY-MM-DD HH:MM:SS'
                if len(fecha_debit) == 19:
                    fecha_debit = fecha_debit[:11] + hora_prueba
                try:
                    fecha_debit_dt = datetime.strptime(fecha_debit, "%Y-%m-%d")
                    # Ahora puedes modificar la hora manualmente
                    fecha_debit_dt = fecha_debit_dt.replace(hour=16, minute=58, second=0)
                    
                    logger.debug(f"hora seteada manualmente para la programacion y prueba para el movimiento de dinero = {fecha_debit_dt} \n")
                    
                except ValueError:
                    raise Exception("El campo date_debit no tiene un formato válido (YYYY-MM-DD)")
            elif isinstance(fecha_debit, datetime):
                # Si ya es datetime, puedes reemplazar la hora usando replace()
                fecha_debit_dt = fecha_debit.replace(hour=16, minute=55, second=0)  # <-- Cambia aquí la hora
            else:
                raise Exception("El campo date_debit no es un string ni un datetime válido")

            print(f"Formato de la Fecha final luego de las validaciones, que usará en el apscheduler = {fecha_debit_dt} \n")
            


            # Programar la ejecución del movimiento de dinero usando APScheduler
            self.scheduler.add_job(
                self.__class__.send_money_movements,  # método estático serializable
                "date", # Ejecutar en una fecha específica
                run_date=fecha_debit_dt, # Fecha y hora de ejecución
                args=[item],
                id=f"movimiento_id_client_{item.get('destination_id')}_{fecha_debit_dt}",
                replace_existing=True,
            )
            logger.debug(f"Tarea programada para {item.get("destination_id")} el {fecha_debit_dt} \n")

def generator_id(test, index):
        prefij = f"{test}{index}"
        current_day = datetime.now().day
        format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
        uid = uuid.uuid4().hex[:4]
        id_returned = f"{prefij}{format_day}{uid}"
        return id_returned
    
    
    
    