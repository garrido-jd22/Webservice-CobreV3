import logging
from flask import jsonify
from Database.database import Session
from datetime import datetime
import uuid
from Models.Money_movement import DirectDebitMovement
from Controllers.cobre_v3_MM_controller import (
    CobreV3MoneyMovement as CobreV3MoneyMovementController,
)
from Controllers.money_movements_controller import MoneyMovementsController

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SOURCE_ID = "acc_znB5gf46CU"


class MoneyMovementFileController:
    def __init__(self):
        self.session = Session()
        self.cobre_v3_mm = CobreV3MoneyMovementController()
        self.money_movement = MoneyMovementsController()

    def __del__(self):
        self.session.close()

    def read_file_csv_money_movement(self, data_csv):

        logger.debug(
            "Iniciando procesamiento del archivo CSV de movimientos de dinero en el controlador read_file_csv_money_movement"
        )

        try:
            # ---------- GENERA UN ID DE MM ---------
            # id_data_mm = self._generator_id("mm_load_", 1)

            # ---------- PROCESA LOS MOVIMIENTOS DE DINERO ------------
            money_movements = []

            for mm_csv in data_csv:
                # Validación de datos requeridos
                required_fields = [
                    "amount",
                    "date_debit",
                    "reference",
                    "account_number",
                ]
                if not all(field in mm_csv for field in required_fields):
                    logger.error(f"Datos requeridos faltantes en el registro: {mm_csv}")
                    raise ValueError(
                        f"Datos requeridos faltantes en el registro: {mm_csv}"
                    )

                # Validación del monto
                try:
                    amount = int(mm_csv["amount"])
                    if amount <= 0:
                        logger.error(f"El monto debe ser mayor a 0: {amount}")
                        raise ValueError(f"El monto debe ser mayor a 0: {amount}")
                except ValueError as e:
                    logger.error(f"Error en el formato del monto: {e}")
                    continue

                logger.debug(
                    f"creando payload para el movimiento de dinero con datos: {mm_csv}"
                )
                # Crear payload para el movimiento de dinero
                movement = {
                    "source_id": mm_csv["destination_id"],
                    "destination_id": SOURCE_ID,
                    "amount": amount,
                    "date_debit": mm_csv["date_debit"],
                    "metadata": {
                        "description": mm_csv["description"]
                    },
                    "external_id": "DebitProduct"
                }

                money_movements.append(movement)

            if not money_movements:
                logger.error("No se encontraron movimientos válidos para procesar")
                return (
                    jsonify(
                        {"error": "No se encontraron movimientos válidos para procesar"}
                    ),
                    400,
                )

            # --------- ENVIAR EL PAYLOAD A LA RUTINA DE MOVIMIENTOS DE DINERO ----------
            logger.debug(f"Total de movimientos a procesar: {len(money_movements)}")
            logger.debug("Enviando movimientos a la rutina de procesamiento... \n")

            logger.debug(
                f"enviando payload a la rutina de movimientos de dinero:{money_movements}"
            )

            self.cobre_v3_mm.routine_money_movements(money_movements)

            return (
                jsonify(
                    {
                        "message": "Archivo procesado exitosamente",
                        "data": {
                            "total_movements": len(money_movements),
                            "movements": money_movements,
                        },
                    }
                ),
                200,
            )

        except FileNotFoundError:
            return jsonify({"error": "El archivo no fue encontrado."}), 404
        except Exception as e:
            logger.error(f"Error procesando el archivo: {str(e)}")
            return jsonify({"error": f"Error procesando el archivo: {str(e)}"}), 500

    def generator_id(self, test, index):
        prefij = f"{test}{index}"
        current_day = datetime.now().day
        format_day = f"{current_day:02d}"  # Asegura que el día tenga 2 dígitos
        uid = uuid.uuid4().hex[:4]
        id_returned = f"{prefij}{format_day}{uid}"
        return id_returned

    def get_movement_status(self, id_data_load):
        """Obtiene el estado de los movimientos de un cargue específico"""
        try:
            # Aquí implementarías la lógica para consultar el estado de los movimientos
            # basado en el id_data_load
            pass
        except Exception as e:
            logger.error(f"Error consultando estado de movimientos: {str(e)}")
            return jsonify({"error": str(e)}), 500
