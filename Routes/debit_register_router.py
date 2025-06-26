from flask import Blueprint, request
from Controllers.debit_register_controller import DebitRegister

debitRegisterRoutes = Blueprint("debit_register", __name__)


# Routes
@debitRegisterRoutes.route("/list-direct-debit", methods=["GET"])
def get_list_counter_party():
    return DebitRegister().get_all_direct_debit_registrations()


@debitRegisterRoutes.route(
    "/counterparties/<counterparty_id>/direct_debit_registrations", methods=["POST"]
)
def set_direct_debit_registrations(counterparty_id):
    return DebitRegister().set_direct_debit_registrations(counterparty_id, request.json)
