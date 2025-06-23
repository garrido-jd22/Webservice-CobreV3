from flask import Blueprint, request
import time
from datetime import datetime, timedelta

# from Controllers.counter_party_controller import CounterParty
from Controllers.auth_token_controller import Token
from Controllers.counter_parties_controller import CounterParty

AuthTokenRoutes = Blueprint("auth_token", __name__)


def format_time_remaining(seconds):
    if seconds < 60:
        return f"{int(seconds)} segundos"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} {'minuto' if minutes == 1 else 'minutos'}"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        if minutes == 0:
            return f"{hours} {'hora' if hours == 1 else 'horas'}"
        else:
            return f"{hours} {'hora' if hours == 1 else 'horas'} y {minutes} {'minuto' if minutes == 1 else 'minutos'}"


# -- recomendacion --
# esta ruta en especifica debe estar creada en un archivo nuevo
# el archivo debe tener la ruta y el servicio al que estara enlazado para obtener el token
@AuthTokenRoutes.route("/get-token-auth", methods=["GET"])
def get_token_auth():

    try:

        token_data = Token.get_token()
        seconds_remaining = int(token_data["expiration_time"] - time.time())

        return {
            "status": "success",
            "data": {
                "token": token_data["token"],
                "expiration_time": token_data["expiration_time"],
                "expires_in_seconds": seconds_remaining,
                "expires_in_human": format_time_remaining(seconds_remaining),
                "expires_at": datetime.fromtimestamp(
                    token_data["expiration_time"]
                ).strftime("%Y-%m-%d %H:%M:%S"),
            },
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}, 500


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
#         return result

#     except Exception as e:
#         return {"error": "Error al procesar la solicitud", "details": str(e)}, 500
