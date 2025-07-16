from datetime import datetime
import uuid
from Database.database import Session
from Models.Money_movement import DirectDebitMovement
import logging
from datetime import datetime
from flask import jsonify
from Database.database import Session
import logging
from Models.Money_movement  import DirectDebitMovement
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from pytz import timezone

# Cobre V3
#from Controllers.cobre_v3_controller import CobreV3 as CobreV3Controller

session = Session()
# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Reducir el nivel de logging de apscheduler y tzlocal
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('tzlocal').setLevel(logging.WARNING)

SOURCE_ID = "acc_znB5gf46CU"


class MoneyMovementsController:
    def __init__(self):
        self.session = Session()
        #self.cobre_v3 = CobreV3Controller()
        # Configuración del JobStore para persistencia en SQLite
        jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
        # Instancia del scheduler con persistencia y zona horaria específica
        self.scheduler = BackgroundScheduler(jobstores=jobstores, timezone=timezone('America/bogota'))
        self.scheduler.start()

    def __del__(self):
        self.session.close()

    def routine_money_movements(self, payload_list):
        
        print("++++++ Iniciando rutina de movimientos de dinero ++++++ \n")
        print("### validación de payload_list \n")
        for item in payload_list:
            #recorrer payload_list
            print(f"Procesando el item: {item} y el id counterparty {item.get("destination_id")}  \n")
        
        for item in payload_list:
            
            fecha_debit = item.get("date_debit")
            
            print(f"Procesando el formato de la fecha inicial dentro de la interacion = {fecha_debit} \n")
            
            if not fecha_debit:
                raise Exception("No se encontró la llave 'date_debit' en el payload")
            # Si la fecha viene como string con formato completo, puedes modificar la hora aquí
            if isinstance(fecha_debit, str):
                # Cambia aquí la hora que quieras probar
                hora_prueba = "16:19:00"  # <-- Cambiar esto para pruebas
                
                # Si el string ya tiene formato 'YYYY-MM-DD HH:MM:SS'
                if len(fecha_debit) == 19:
                    fecha_debit = fecha_debit[:11] + hora_prueba
                try:
                    fecha_debit_dt = datetime.strptime(fecha_debit, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    raise Exception("El campo date_debit no tiene un formato válido (YYYY-MM-DD HH:MM:SS)")
            elif isinstance(fecha_debit, datetime):
                # Si ya es datetime, puedes reemplazar la hora usando replace()
                fecha_debit_dt = fecha_debit.replace(hour=8, minute=41, second=0)  # <-- Cambia aquí la hora
            else:
                raise Exception("El campo date_debit no es un string ni un datetime válido")

            print(f"Formato de la Fecha final que usará en el apscheduler = {fecha_debit_dt} \n")
            


            # Programar la ejecución del movimiento de dinero usando APScheduler
            self.scheduler.add_job(
                self.__class__.ejecutar_movimiento_job,  # método estático serializable
                "date", # Ejecutar en una fecha específica
                run_date=fecha_debit_dt, # Fecha y hora de ejecución
                args=[item],
                id=f"movimiento_id_client_{item.get('destination_id')}_{fecha_debit_dt}",
                replace_existing=True,
            )
            logger.debug(
                f"Tarea programada para {item.get("destination_id")} el {fecha_debit_dt} \n"
            )
    
    
    @staticmethod
    def ejecutar_movimiento_job(payload):
        """
        Método estático para ejecutar el movimiento de dinero, serializable por APScheduler.
        Crea una nueva sesión SQLAlchemy en cada ejecución.
        """
        session_local = Session()
        try:
            money_movement = []
            count = 0
            
            #for item in payload:
            logger.info(f"[APScheduler] Ejecutando movimiento de dinero para: {payload} \n")
                
            #count += 1
                
            money_movement = DirectDebitMovement(
                id=generator_id("mm_00",count),  # Genera un ID único para el movimiento
                source_id=SOURCE_ID,
                destination_id=payload["destination_id"],
                amount=payload["amount"],
                date_debit=payload["date_debit"],
                description=payload["metadata"]["description"],
                reference_debit=payload["metadata"]["reference"],
                checker_approval=payload["checker_approval"],
                hora_fecha_exacta_movimiento =datetime.now(),
            )

            session_local.add(money_movement)
            session_local.commit()
            
            logger.info(f"[APScheduler] Movimiento programado guardado en la base de datos: {money_movement.to_dict()} \n")
            
            print({"message": "movimientos programados ingresados en la tabla correctamente."})
        except Exception as e:
            session_local.rollback()
            logger.error(f"[APScheduler] Error al guardar el movimiento: {e} \n")
            logger.debug(f"Error al guardar el movimiento ={e} \n")
        finally:
            session_local.close()

def generator_id(test, index):
    prefij = f"{test}{index}"
    current_day = datetime.now().day
    format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
    uid = uuid.uuid4().hex[:4]
    id_returned = f"{prefij}{format_day}{uid}"
    return id_returned