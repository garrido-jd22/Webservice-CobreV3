from flask import Blueprint

from Controllers.counter_party_controller import CounterParty

counterPartyRoutes = Blueprint('counter_party', __name__)

@counterPartyRoutes.route('/list-counterparty', methods=['GET'])
def get_list_counter_party():
    return CounterParty().get_all_counter_party()