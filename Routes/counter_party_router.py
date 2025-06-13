from flask import Blueprint

from Controllers.counter_party_controller import CounterParty
from Controllers.cobre_controller import Cobre

counterPartyRoutes = Blueprint('counter_party', __name__)

@counterPartyRoutes.route('/get-token-cobre', methods=['GET'])
def get_token_cobre():
    return Cobre().get_cobre_token()

@counterPartyRoutes.route('/list-counterparty', methods=['GET'])
def get_list_counter_party():
    return CounterParty().get_all_counter_party()