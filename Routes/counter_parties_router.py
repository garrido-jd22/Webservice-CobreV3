# from flask import Blueprint, request
# import time
# from datetime import datetime, timedelta

# # from Controllers.counter_party_controller import CounterParty
# from Controllers.auth_token_controller import Token
# from Controllers.counter_parties_controller import CounterParty
# from Controllers.debit_register_controller import debit_register

# counterPartyRoutes = Blueprint("counter_parties", __name__)


# # llega un json a la ruta post
# @counterPartyRoutes.route("/counterparties", methods=["POST"])
# def create_counter_party():
#     try:
#         # Obtener los datos del cuerpo de la petición
#         data = request.get_json()

#         # # Validar los campos requeridos
#         # required_fields = [
#         #     "geo",
#         #     "type",
#         #     "alias",
#         #     "counterparty_fullname",
#         #     "beneficiary_institution",
#         #     "account_number",
#         #     "counterparty_id_type",
#         #     "counterparty_id_number",
#         #     "counterparty_phone",
#         #     "counterparty_email",
#         # ]

#         # missing_fields = [field for field in required_fields if field not in data]
#         # if missing_fields:
#         #     return {
#         #         "error": "Campos requeridos faltantes",
#         #         "missing_fields": missing_fields,
#         #     }, 400

#         # Crear el counter party
#         result = CounterParty().set_counter_party(data)
#         # pasarle la respuesta de la creacion del counterparty concretamente el id unico del counter party
#         # para crear un registro para debitarle al counterparty
#         debit_register().set_direct_debit(result)

#         return result

#     except Exception as e:
#         return {"error": "Error al procesar la solicitud", "details": str(e)}, 500
