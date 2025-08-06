import csv
import io
import re
from flask import Blueprint, jsonify, request
from datetime import datetime

from Controllers.counter_party_controller import CounterParty
from Controllers.management_file_controller import ManagementFileController
from Controllers.management_file_cobre_v3_controller import (
    ManagementFileCobreV3Controller,
)
from Controllers.counter_party_controller import CounterParty
from Controllers.auth_token_controller import Token

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

        # Definir columnas esperadas
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
        telefono_regex = r"^\+57\d{10}$"  # +57 seguido de 10 dígitos

        for idx, fila in enumerate(
            data_csv, start=2
        ):  # start=2 por encabezado en línea 1
            for columna in columnas_esperadas:
                if columna not in fila:
                    errores.append(f"Columna '{columna}' faltante en la fila {idx}.")
                    continue

                valor = fila[columna].strip() if fila[columna] else ""

                # Validaciones generales de campos obligatorios
                if (
                    columna
                    in [
                        "geo",
                        "type",
                        "alias",
                        "counterparty_fullname",
                        "counterparty_id_type",
                        "counterparty_phone",
                    ]
                    and not valor
                ):
                    errores.append(
                        f"El campo '{columna}' no puede estar vacío en la fila {idx}."
                    )

                # Validación de campos numéricos
                elif columna == "account_number":
                    if not valor.isdigit():
                        errores.append(
                            f"El campo 'account_number' debe ser numérico en la fila {idx}."
                        )
                    elif len(valor) > 20:
                        errores.append(
                            f"El campo 'account_number' debe tener máximo 20 caracteres en la fila {idx}."
                        )

                elif (
                    columna == "beneficiary_institution"
                    or columna == "counterparty_id_number"
                ):
                    if not valor.isdigit():
                        errores.append(
                            f"El campo '{columna}' debe ser numérico en la fila {idx}."
                        )

                # Validación de teléfono
                elif columna == "counterparty_phone":
                    if not re.match(telefono_regex, valor):
                        errores.append(
                            f"El campo 'counterparty_phone' debe tener el formato +57XXXXXXXXXX en la fila {idx}."
                        )

                # Validación de correo electrónico
                elif columna == "counterparty_email":
                    if not re.match(email_regex, valor):
                        errores.append(
                            f"El campo 'counterparty_email' no es un correo válido en la fila {idx}."
                        )

        if errores:
            return jsonify({"errores": errores}), 400

        # TOKEN COBRE V3
        requestbody = {
            "user_id": request.form.get("User-ID"),
            "secret": request.form.get("Secret"),
        }

        Token().get_token(requestbody)
        data_saved = ManagementFileCobreV3Controller().read_file_csv_cobre_v3(data_csv)

        return data_saved

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@counterPartyRoutes.route("/get-counterparty-id-load/<id_load>", methods=["GET"])
def get_counter_party_by_id_load(id_load):
    return CounterParty().get_counter_party_by_id_load(id_load)
