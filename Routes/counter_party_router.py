import csv
import io
import re
from flask import Blueprint, jsonify, request

from Controllers.counter_party_controller import CounterParty
from Controllers.management_file_controller import ManagementFileController
from Controllers.counter_party_controller import CounterParty

counterPartyRoutes = Blueprint("counter_party", __name__)


@counterPartyRoutes.route("/list-counterparty", methods=["GET"])
def get_list_counter_party():
    return CounterParty().get_all_counter_party()


@counterPartyRoutes.route("/get-counterparty/<id>", methods=["GET"])
def get_counter_party(id):
    return CounterParty().get_counter_party(id)


@counterPartyRoutes.route("/process-csv", methods=["POST"])
def process_csv_file():
    try:

        if "file" not in request.files:
            return "Archivo no recibido", 400

        archivo = request.files["file"]

        # Leer el contenido como texto usando io.TextIOWrapper
        archivo_stream = io.StringIO(archivo.stream.read().decode("utf-8-sig"))

        # Leer como CSV
        lector_csv = csv.DictReader(archivo_stream)
        data_csv = list(lector_csv)

        # Definir columnas esperadas y sus validaciones
        columnas_esperadas = [
            "geo",
            "type",
            "alias",
            "beneficiary_institution",
            "account_number",
            "counterparty_fullname",
            "counterparty_id_type",
            "counterparty_id_number",
            "counterparty_phone",
            "counterparty_email",
        ]

        errores = []
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        for idx, fila in enumerate(
            data_csv, start=2
        ):  # start=2 para considerar encabezado en la línea 1
            for columna in columnas_esperadas:
                if columna not in fila:
                    errores.append(f"Columna '{columna}' faltante en la fila {idx}.")
                    continue
                valor = fila[columna].strip() if fila[columna] else ""
                # Validaciones por columna
                if columna in [
                    "geo",
                    "type",
                    "alias",
                    "beneficiary_institution",
                    "counterparty_fullname",
                    "counterparty_id_type",
                ]:
                    if not valor:
                        errores.append(
                            f"El campo '{columna}' no puede estar vacío en la fila {idx}."
                        )
                elif columna in [
                    "account_number",
                    "counterparty_id_number",
                    "counterparty_phone",
                ]:
                    if not valor.isdigit():
                        errores.append(
                            f"El campo '{columna}' debe ser numérico en la fila {idx}."
                        )
                elif columna == "counterparty_email":
                    if not re.match(email_regex, valor):
                        errores.append(
                            f"El campo 'counterparty_email' no es un correo válido en la fila {idx}."
                        )

        if errores:
            return jsonify({"errores": errores}), 400

        data_saved = ManagementFileController().read_file_csv(data_csv)

        return data_saved

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@counterPartyRoutes.route("/get-counterparty-id-load/<id_load>", methods=["GET"])
def get_counter_party_by_id_load(id_load):
    return CounterParty().get_counter_party_by_id_load(id_load)
