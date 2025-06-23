from flask import Blueprint, request, jsonify

from Controllers.counter_party_controller import CounterParty
from Controllers.management_file_controller import ManagementFileController
from Controllers.counter_party_controller import CounterParty

counterPartyRoutes = Blueprint("counter_party", __name__)


@counterPartyRoutes.route("/list-counterparty", methods=["GET"])
def get_list_counter_party():
    return CounterParty().get_all_counter_party()


# se crea un endpoint que acepta la peticion post y un parametro que es la ruta al archivo csv
@counterPartyRoutes.route("/process-csv/<path:file_path>", methods=["POST"])
def process_csv_file(file_path):
    try:
        # se le inserta como argumento la ruta (path) del archivo y nos devuelve un json de esos datos y una lista de esos datos
        datos_csv = ManagementFileController().read_file_csv(file_path)
        print("datos de respuesta del file management controller = ", datos_csv)

        return datos_csv

    except Exception as e:
        return jsonify({"error": str(e)}), 500
