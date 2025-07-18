from flask import Blueprint, request, jsonify
from Controllers.money_movement_file_controller import MoneyMovementFileController
import csv
import io
import re
from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

moneyMovementRoutes = Blueprint("money_movement", __name__)


@moneyMovementRoutes.route("/send-moneymovement", methods=["POST"])
def set_money_movement():
    try:
        
        if "file" not in request.files:
            logger.error("Archivo no recibido en la solicitud")
            return jsonify({"error": "Archivo no recibido"}), 400
        
        archivo = request.files["file"]

        # Leer el contenido como texto usando io.TextIOWrapper
        archivo_stream = io.StringIO(archivo.stream.read().decode("utf-8-sig"))

        # Leer como CSV
        lector_csv = csv.DictReader(archivo_stream)
        data_csv = list(lector_csv)
        
        
        # Definir columnas esperadas y sus validaciones
        columnas_esperadas = [
            "destination_id",
            "amount",
            "date_debit",
            "reference",
            "description",
            "counterparty_fullname",
            "counterparty_id_number",
            "account_number",
        ]
        errores = []
        
        # Validar que las columnas esperadas estén presentes
        logger.debug("iterando y Validando columnas del archivo CSV")
        
        for idx, fila in enumerate(
            data_csv, start=2
        ):  # start=2 para considerar encabezado en la línea 1
            # Ignorar filas completamente vacías
            if all((v is None or str(v).strip() == "") for v in fila.values()):
                logger.debug(f"Fila {idx} ignorada por estar vacía.")
                continue
            for columna in columnas_esperadas:
                if columna not in fila:
                    errores.append(f"Columna '{columna}' faltante en la fila {idx}.")
                    logger.error(f"Columna '{columna}' faltante en la fila {idx}.")
                    continue
                valor = fila[columna].strip() if fila[columna] else ""
                # Validaciones por columna
                if not valor:
                    errores.append(f"El campo '{columna}' no puede estar vacío en la fila {idx}.")
                    logger.error(f"El campo '{columna}' no puede estar vacío en la fila {idx}.")
                    continue
                if columna == "amount":
                    try:
                        float(valor)
                    except ValueError:
                        errores.append(f"El campo 'amount' debe ser numérico (puede tener decimales) en la fila {idx}.")
                        logger.error(f"El campo 'amount' debe ser numérico (puede tener decimales) en la fila {idx}.")
                        
                elif columna in ["account_number", "counterparty_id_number"]:
                    if not valor.isdigit():
                        errores.append(f"El campo '{columna}' debe ser numérico en la fila {idx}.")
                        logger.error(f"El campo '{columna}' debe ser numérico en la fila {idx}.")
                        
                elif columna == "date_debit":
                    try:
                        fecha_debito = datetime.strptime(valor, "%Y-%m-%d").date()
                        if fecha_debito < datetime.now().date():
                            errores.append(f"El campo 'date_debit' tiene una fecha menor a la fecha actual en la fila {idx}.")
                            logger.error(f"El campo 'date_debit' tiene una fecha menor a la fecha actual en la fila {idx}.")
                    except ValueError:
                        errores.append(f"El campo 'date_debit' tiene un formato de fecha inválido en la fila {idx}.")
                        logger.error(f"El campo 'date_debit' tiene un formato de fecha inválido en la fila {idx}.")
        
        if errores:
            logger.error(f"Errores encontrados en el archivo: {errores}")
            return jsonify({"errores": errores}), 400
        
        logger.debug("Todas las columnas requeridas están presentes y validadas correctamente enviando el archivo al controlador")
        # despues de validar las columnas, se procede a enviar el archivo al controlador
        data_save =  MoneyMovementFileController().read_file_csv_money_movement(data_csv)

        return data_save
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
