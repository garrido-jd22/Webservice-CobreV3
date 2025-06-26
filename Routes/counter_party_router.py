from flask import Blueprint, jsonify

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


@counterPartyRoutes.route("/process-csv/<path:file_path>", methods=["POST"])
def process_csv_file(file_path):
    try:
        datos_csv = ManagementFileController().read_file_csv(file_path)
        print("datos de respuesta del file management controller = ", datos_csv)

        return datos_csv

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@counterPartyRoutes.route("/get-counterparty-id-load/<id_load>", methods=["GET"])
def get_counter_party_by_id_load(id_load):
    return CounterParty().get_counter_party_by_id_load(id_load)
