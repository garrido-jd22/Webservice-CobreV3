import logging
from flask import jsonify
import requests
from requests.adapters import HTTPAdapter
from Controllers.auth_token_controller import Token as CobreToken
from concurrent.futures import ThreadPoolExecutor, as_completed

# Crear un session global reutilizable
session = requests.Session()
adapter = HTTPAdapter(pool_connections=300, pool_maxsize=300)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
SOURCE_ID = "acc_znB5gf46CU"

from dotenv import load_dotenv
import os

load_dotenv()


class CobreV3CounterParty:

    BASE_URL = "https://api.cobre.co/v1"
    MESSAGE_ERROR = {"error": "No se pudo obtener el token de autenticación"}
    CONTENT_TYPE = "application/json"

    def __init__(self):
        self.token = CobreToken()
        self.session = session

    # Destructor de la clase
    def __del__(self):
        self.session.close()

    def get_cobre_v3_counterparty(self):
        try:
            response_token = self.token.get_token({})
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties?sensitive_data=true"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def get_cobre_v3_counterparty_by_id_number(self, cp_item):
        try:
            response_token = self.token.get_token({})
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties?counterparty_id_number={cp_item['counterparty_id_number']}&beneficiary_institution={cp_item['beneficiary_institution']}&account_number={cp_item['account_number']}&sensitive_data=true"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            contents = response.json().get("contents", [])

            if contents:
                response_body = contents[0]
                return response_body
            else:
                # Puedes retornar None, un mensaje, o lanzar una excepción controlada
                return None  # o: return {"error": "No se encontraron elementos en contents"}
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def filter_counter_party_id_number(self, list_counterparty):
        result = []
        with ThreadPoolExecutor(
            max_workers=len(list_counterparty)
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(
                    self.get_cobre_v3_counterparty_by_id_number,
                    cp,
                )
                for cp in list_counterparty
            ]

            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result

    def delete_cobre_v3_counterparty(self, id_counterparty):
        try:
            requestbody = {
                "user_id": os.environ["USER_ID"],
                "secret": os.environ["SECRET"],
            }
            response_token = self.token.get_token(requestbody)
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties/{id_counterparty}"
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return jsonify({"success": "Counter Party eliminado exitosamente."}), 204
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def delete_all_counterparties(self, list_id_cp):
        result = []
        with ThreadPoolExecutor(
            max_workers=len(list_id_cp)
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(self.delete_cobre_v3_counterparty, cp["id"])
                for cp in list_id_cp
            ]

            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result

    def set_cobre_v3_counterparty(self, item_counterparty):
        try:
            requestbody = {
                "user_id": os.environ["USER_ID"],
                "secret": os.environ["SECRET"],
            }
            response_token = self.token.get_token(requestbody)
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties"
            response = self.session.post(
                url, headers=headers, json=item_counterparty, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return jsonify({"error": e}), 409
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def send_all_counterparties(self, list_counterparty):
        result = []
        with ThreadPoolExecutor(
            max_workers=len(list_counterparty)
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(self.set_cobre_v3_counterparty, cp)
                for cp in list_counterparty
            ]

            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result
