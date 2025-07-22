import logging
from flask import jsonify
import requests
import time
from Controllers.auth_token_controller import Token as CobreToken
from concurrent.futures import ThreadPoolExecutor, as_completed
from Database.database import Session

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
SOURCE_ID = "acc_znB5gf46CU"


class CobreV3CounterParty:

    BASE_URL = "https://api.cobre.co/v1"
    MESSAGE_ERROR = {"error": "No se pudo obtener el token de autenticación"}
    CONTENT_TYPE = "application/json"

    def __init__(self):
        self.token = CobreToken()
        self.session = requests.Session()

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

    def get_cobre_v3_counterparty_by_id_number(self, id_number):
        try:
            response_token = self.token.get_token({})
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties?counterparty_id_number={id_number}&sensitive_data=true"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            counter_party_content = {
                "counterparty_id_number": id_number,
                "exist": response.json()["contents"],
            }

            return counter_party_content
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def filter_counter_party_id_number(self, lista_counterparties):
        result = []
        with ThreadPoolExecutor(
            max_workers=100
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(
                    self.get_cobre_v3_counterparty_by_id_number,
                    cp["counterparty_id_number"],
                )
                for cp in lista_counterparties
            ]

            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result

    def delete_cobre_v3_counterparty(self, id_counterparty):
        try:
            response_token = self.token.get_token({})
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

    def set_cobre_v3_counterparty(self, item_counterparty):
        try:
            response_token = self.token.get_token({})
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

    def send_all_counterparties(self, lista_counterparties):
        result = []
        with ThreadPoolExecutor(
            max_workers=100
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(self.set_cobre_v3_counterparty, cp)
                for cp in lista_counterparties
            ]

            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result
