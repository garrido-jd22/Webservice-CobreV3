from flask import Blueprint, request
from Controllers.cobre_v3_controller import CobreV3 as CobreV3Controller
from Controllers.cobre_v3_CP_controller import (
    CobreV3CounterParty as CobreV3CounterPartyController,
)

cobreV3Routes = Blueprint("cobre_v3", __name__)


@cobreV3Routes.route("/get-cobre-v3-balance", methods=["GET"])
# @requieres_authentication
def get_cobre_v3_balance():
    return CobreV3Controller().get_cobre_v3_balance()

@cobreV3Routes.route("/get-cobre-v3-counterparty", methods=["GET"])
# @requieres_authentication
def get_cobre_v3_counterparty():
    return CobreV3CounterPartyController().get_cobre_v3_counterparty()


@cobreV3Routes.route("/set-cobre-v3-counterparty", methods=["POST"])
# @requieres_authentication
def set_cobre_v3_counterparty():
    return CobreV3CounterPartyController().set_cobre_v3_counterparty(request.json)


@cobreV3Routes.route(
    "/delete-cobre-v3-counterparty/<counterparty_id>", methods=["DELETE"]
)
# @requieres_authentication
def delete_cobre_v3_counterparty(counterparty_id):
    return CobreV3CounterPartyController().delete_cobre_v3_counterparty(counterparty_id)
