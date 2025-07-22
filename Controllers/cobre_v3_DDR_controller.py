import logging
from flask import jsonify
import requests
import time
from Controllers.auth_token_controller import Token as CobreToken
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
SOURCE_ID = "acc_znB5gf46CU"


class CobreV3DirectDebit:

    BASE_URL = "https://api.cobre.co/v1"
    MESSAGE_ERROR = {"error": "No se pudo obtener el token de autenticación"}
    CONTENT_TYPE = "application/json"

    def __init__(self):
        self.token = CobreToken()
        self.session = requests.Session()

    def get_cobre_v3_direct_debit_by_id(self, counterparty_id, ddr):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties/{counterparty_id}/direct_debit_registrations/{ddr}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al consumir API de Cobre: {e}")
            return jsonify({"error": e}), 500

    def filter_direct_debit_by_id(self, list_ddr):
        result = []
        with ThreadPoolExecutor(
            max_workers=100
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(
                    self.get_cobre_v3_direct_debit_by_id,
                    item["destination_id"],
                    item["id"],
                )
                for item in list_ddr
            ]

            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result

    def set_cobre_v3_direct_debit(self, item_direct_debit, counterparty_id):
        try:
            response_token = self.token.get_token()
            token = response_token.get("token")

            if not token:
                return self.MESSAGE_ERROR

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": self.CONTENT_TYPE,
            }

            url = f"{self.BASE_URL}/counterparties/{counterparty_id}/direct_debit_registrations"
            response = self.session.post(
                url, headers=headers, json=item_direct_debit, timeout=10
            )
            response.raise_for_status()
            time.sleep(
                0.5
            )  # Espera medio segundo entre cada solicitud para evitar sobrecargar la API
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.debug("-------------------ERROR-----------------")
            logger.debug("-------------------ERROR-----------------")
            logger.debug(response.json())
            logger.debug("-----------------------------------------")
            logger.debug("-----------------------------------------")
            return jsonify({"error": response.json()}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"error": e}), 500

    def send_all_direct_debit(self, list_debit_id_cp):
        ddr_list, id_cp_list = list_debit_id_cp
        result = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            future_to_id_cp = {
                executor.submit(self.set_cobre_v3_direct_debit, ddr, id_cp): id_cp
                for ddr, id_cp in zip(ddr_list, id_cp_list)
            }

            for future in as_completed(future_to_id_cp):
                id_cp = future_to_id_cp[future]
                try:
                    result.append({"id_cp": id_cp, **future.result()})
                except Exception as e:
                    result.append({"id_cp": id_cp, "error": str(e)})
        return result