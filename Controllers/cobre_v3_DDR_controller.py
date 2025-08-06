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


class CobreV3DirectDebit:

    BASE_URL = "https://api.cobre.co/v1"
    MESSAGE_ERROR = {"error": "No se pudo obtener el token de autenticación"}
    CONTENT_TYPE = "application/json"

    def __init__(self):
        self.token = CobreToken()
        self.session = session

    # Destructor de la clase
    def __del__(self):
        self.session.close()

    def get_cobre_v3_direct_debit_by_id(self, counterparty_id, ddr):
        try:
            response_token = self.token.get_token({})
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
            max_workers=len(list_ddr)
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

    def set_cobre_v3_direct_debit(self, item_direct_debit):
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

            url = f"{self.BASE_URL}/counterparties/{item_direct_debit['id_cp']}/direct_debit_registrations"
            response = self.session.post(
                url,
                headers=headers,
                json={
                    "destination_id": item_direct_debit["destination_id"],
                    "registration_description": item_direct_debit[
                        "registration_description"
                    ],
                },
                timeout=10,
            )
            response.raise_for_status()
            data_ddr = response.json()
            data_ddr["id_cp"] = item_direct_debit["id_cp"]
            return data_ddr
        except requests.exceptions.HTTPError as e:
            logger.debug("-------------------ERROR-----------------")
            logger.debug("-------------------ERROR-----------------")
            logger.debug(f"Error {e}")
            logger.debug(response.json())
            logger.debug("-----------------------------------------")
            logger.debug("-----------------------------------------")
            return jsonify({"error": response.json()}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"error": e}), 500

    def send_all_direct_debit(self, list_debit):
        result = []
        with ThreadPoolExecutor(
            max_workers=len(list_debit)
        ) as executor:  # max_workers=5: significa que se harán máximo 10 peticiones al mismo tiempo.
            futures = [
                executor.submit(self.set_cobre_v3_direct_debit, ddr)
                for ddr in list_debit
            ]

            for future in as_completed(
                futures
            ):  # as_completed permite iterar sobre los resultados a medida que se completan
                result.append(future.result())
        return result
