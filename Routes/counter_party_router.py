import csv
import io
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

        datos_csv = ManagementFileController().read_file_csv(data_csv)
        print("datos de respuesta del file management controller = ", datos_csv)

        return datos_csv

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@counterPartyRoutes.route("/get-counterparty-id-load/<id_load>", methods=["GET"])
def get_counter_party_by_id_load(id_load):
    return CounterParty().get_counter_party_by_id_load(id_load)
