from flask import Blueprint, request
import time
from datetime import datetime, timedelta

# from Controllers.counter_party_controller import CounterParty
from Controllers.auth_token_controller import Cobre
from Controllers.cobre_balance_controller import Cobre_balance

cobreBalanceRoutes = Blueprint("cobre_balance", __name__)


# obtener cuenta cobre para validar si existe y utilizar para la debitacion
@cobreBalanceRoutes.route("/get-cobre-balance-id/<id>", methods=["GET"])
def get_cobre_balance_id(id):
    try:
        if not id:
            return {"error": "ID de cuenta requerido"}, 400

        # obtener cuenta cobre balance
        result = Cobre_balance().get_cobre_balance(id)
        return result

    except Exception as e:
        return {"error": "Error al procesar la solicitud", "details": str(e)}, 500


# ruta para crear una billetera virtual/cuenta cobre si no existe
@cobreBalanceRoutes.route("/create-cobrebalance", methods=["POST"])
def create_cobre_balance():

    try:
        # Obtener los datos del cuerpo de la petición
        data = request.get_json()

        # # Validar los campos requeridos
        # required_fields = [
        # "provider_id",
        # "action",
        # "alias"
        # ]

        # missing_fields = [field for field in required_fields if field not in data]
        # if missing_fields:
        #     return {
        #         "error": "Campos requeridos faltantes",
        #         "missing_fields": missing_fields,
        #     }, 400

        # validar si existe una cuenta cobre balance

        # Crear el counter party
        result = Cobre_balance().set_cobre_balance(data)
        return result

    except Exception as e:
        return {"error": "Error al procesar la solicitud", "details": str(e)}, 500


# @app.get("/counter_party")
# def list_counter_parties():
#     with SessionLocal() as db:
#         result = get_all_counter_parties(db)
#         return jsonify([p.to_dict() for p in result]), 200
