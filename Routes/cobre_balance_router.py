from flask import Blueprint
from Controllers.cobre_balance_controller import CobreBalance

cobreBalanceRoutes = Blueprint("cobre_balance", __name__)

@cobreBalanceRoutes.route("/get-cobre-balance/<id>", methods=["GET"])
def get_cobre_balance(id):
    try:
        if not id:
            return {"error": "ID de cuenta requerido"}, 400
        
        result = CobreBalance().get_cobre_balance(id)
        return result

    except Exception as e:
        return {"error": "Error al procesar la solicitud", "details": str(e)}, 500
