import logging

from flask import jsonify
import requests
from Controllers.auth_token_controller import Token as CobreToken

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CobreV3:

    BASE_URL = "https://api.cobre.co/v1"

    def __init__(self):
        self.token = CobreToken()

    def get_cobre_v3_balance(self):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return {"error": "No se pudo obtener el token de autenticación"}

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            url = f"{self.BASE_URL}/accounts"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": "Error al consumir API de Cobre"}), 500

    def get_cobre_v3_counterparty(self):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return {"error": "No se pudo obtener el token de autenticación"}

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            url = f"{self.BASE_URL}/counterparties"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": "Error al consumir API de Cobre"}), 500

    def set_cobre_v3_counterparty(self, data_counterparty):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return {"error": "No se pudo obtener el token de autenticación"}

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            url = f"{self.BASE_URL}/counterparties"
            response = requests.post(url, headers=headers, json=data_counterparty)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": "Error al consumir API de Cobre"}), 500

    def delete_cobre_v3_counterparty(self, id_counterparty):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return {"error": "No se pudo obtener el token de autenticación"}

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            url = f"{self.BASE_URL}/counterparties/{id_counterparty}"
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return jsonify({"success": "Counter Party eliminado exitosamente."}), 204
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": "Error al consumir API de Cobre"}), 500
