from flask import Blueprint, request
from Controllers.debit_register_controller import DebitRegister
from Controllers.management_file_cobre_v3_controller import ManagementFileCobreV3Controller

debitRegisterRoutes = Blueprint("debit_register", __name__)


# Routes
@debitRegisterRoutes.route("/list-direct-debit", methods=["GET"])
def get_list_counter_party():
    return DebitRegister().get_all_direct_debit_registrations()

@debitRegisterRoutes.route("/export-direct-debit/<created_at>", methods=["GET"])
def get_debit_register_create_at(created_at):
    return ManagementFileCobreV3Controller().export_file_csv_cobre_v3_ddr(created_at)

@debitRegisterRoutes.route(
    "/counterparties/<counterparty_id>/direct_debit_registrations", methods=["POST"]
)
def set_direct_debit_registrations(counterparty_id):
    return DebitRegister().set_direct_debit_registrations(counterparty_id, request.json)
