from flask import Blueprint, request
from Controllers.debit_register_controller import debit_register

debitRegisterRoutes = Blueprint("debit_register", __name__)


# Routes
@debitRegisterRoutes.route(
    "/counterparties/<counterparty_id>/direct_debit_registrations", methods=["POST"]
)
def set_direct_debit_registrations(counterparty_id):
    return False
