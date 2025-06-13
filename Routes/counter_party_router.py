from flask import Blueprint, request, jsonify

from Controllers.counter_party_controller import CounterParty
from Controllers.management_file_controller import ManagementFileController

counterPartyRoutes = Blueprint('counter_party', __name__)

@counterPartyRoutes.route('/list-counterparty', methods=['GET'])
def get_list_counter_party():
    return CounterParty().get_all_counter_party()

#se crea un endpoint que acepta la peticion post y un parametro que es la ruta al archivo csv
@counterPartyRoutes.route('/process-csv/<path:file_path>', methods=['POST'])
def process_csv_file(file_path):
    try:

        return ManagementFileController().read_file_csv(file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500