from flask import Blueprint, request, jsonify
from Controllers.money_movements_controller import MoneyMovementsController

moneyMovementRoutes = Blueprint("money_movement", __name__)


@moneyMovementRoutes.route("/set-money-movement/<extra_string>", methods=["GET"])
def set_money_movement(extra_string):
    try:
        data = request.get_json(force=True)
        controller = MoneyMovementsController()
        payload = controller.set_money_movement(data, extra_string)
        return jsonify(payload), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
