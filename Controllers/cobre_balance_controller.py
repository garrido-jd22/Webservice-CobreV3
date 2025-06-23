from flask import jsonify

# from Database.database import Session  # Comentado: No se usa base de datos local
# from Models.counter_party import CounterParty as CounterPartyModel  # Comentado: Solo como referencia
import json
import requests
import logging
from Controllers.auth_token_controller import Cobre

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Cobre_balance:

    def __init__(self):

        self.cobre_api_url = "https://api.qa.cobre.co"

    # crear una nueva cobre_balance
    def set_cobre_balance(self, data):
        """
        Método para crear un nuevo cobre balance (cuenta donde llegaran los debitos automaticos) en la API de Cobre

        Args:
            data (dict): Datos de cobre balance a crear

        Returns:
            tuple: (response_json, status_code)
        """
        try:
            # Paso 1: Obtener token de autenticación
            logger.info(
                "Obteniendo token de autenticación desde el servicio de token..."
            )
            cobre = Cobre()
            token_data = cobre.get_cobre_token()
            print(
                "\n token obtenido desde el servicio token : \n ",
                token_data["token"],
                "\n",
            )

            # Verificar que el token se obtuvo correctamente
            if not token_data or "token" not in token_data:
                logger.error("Error: No se pudo obtener el token de autenticación")
                return (
                    jsonify(
                        {
                            "error": "No se pudo obtener el token de autenticación",
                            "details": "El token es requerido para autenticar la petición",
                        }
                    ),
                    401,
                )

            # Paso 2: Preparar headers de la petición
            logger.info("Preparando headers de la petición...")
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token_data['token']}",
            }

            # Paso 3: Preparar el payload según la documentación de la API
            logger.info("Preparando payload de la petición...")
            try:
                # Obtener los datos del metadata directamente del objeto data
                metadata = data.get("metadata", {})

                # Asegurarnos de que los datos estén en el formato correcto
                payload = {
                    "provider_id": data.get("provider_id"),
                    "action": data.get("action"),
                    "metadata": {"alias": metadata.get("alias")},
                }

                # Convertir el payload a JSON string para logging
                payload_json = json.dumps(payload)
                logger.debug(f" ## Payload preparado ## :\n {payload_json}\n")

            except Exception as e:
                logger.error(f"Error al preparar el payload: {str(e)}")
                return (
                    jsonify(
                        {
                            "error": "Error al preparar los datos de la petición",
                            "details": str(e),
                        }
                    ),
                    400,
                )
            logger.debug(
                f" ## Peticion completa para enviar a la api ## :\n payload: {payload_json} \n headers:{headers} \n data: {payload} \n"
            )
            # Paso 4: Realizar la petición a la API
            logger.info("Enviando petición a la API...")
            try:
                response = requests.post(
                    url=f"{self.cobre_api_url}/v1/accounts",
                    headers=headers,
                    json=payload,
                )
                logger.debug(
                    f"Respuesta de la API - Status Code: {response.status_code} \n "
                )
                logger.debug(f"Respuesta de la API - Headers: {response.headers}\n")
                logger.debug(f"Respuesta de la API - Body: {response.text}\n")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error en la petición HTTP: {str(e)}")
                return (
                    jsonify(
                        {"error": "Error de conexión con la API", "details": str(e)}
                    ),
                    500,
                )

            # Paso 5: Procesar la respuesta
            if response.status_code == 200 or response.status_code == 201:
                logger.info("Cobre balance creado exitosamente")
                return (
                    jsonify(
                        {
                            "message": "Cobre balance creado exitosamente",
                            "data": response.json(),
                        }
                    ),
                    201,
                )
            else:
                error_response = (
                    response.json()
                    if response.text
                    else {"message": "Error desconocido"}
                )
                logger.error(f"Error en la respuesta de la API: {error_response}")
                return (
                    jsonify(
                        {
                            "error": "Error el cobre balance en la API externa",
                            "details": error_response,
                            "status_code": response.status_code,
                        }
                    ),
                    response.status_code,
                )

        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return (
                jsonify({"error": "Error al procesar la solicitud", "details": str(e)}),
                500,
            )

    # obtener cuenta cobre balance por id
    def get_cobre_balance(self, id):
        """
        Método para obtener el balance de una cuenta Cobre

        Args:
            id (str): ID de la cuenta Cobre

        Returns:
            tuple: (response_json, status_code)
        """
        try:
            # Paso 1: Obtener token de autenticación
            logger.info("Obteniendo token de autenticación...")
            cobre = Cobre()
            token_data = cobre.get_cobre_token()

            # Verificar que el token se obtuvo correctamente
            if not token_data or "token" not in token_data:
                logger.error("Error: No se pudo obtener el token de autenticación")
                return (
                    jsonify(
                        {
                            "error": "No se pudo obtener el token de autenticación",
                            "details": "El token es requerido para autenticar la petición",
                        }
                    ),
                    401,
                )

            # Paso 2: Preparar headers de la petición
            logger.info("Preparando headers de la petición...")
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token_data['token']}",
            }

            # Paso 3: Realizar la petición a la API
            logger.info(
                f"Enviando petición a la API para obtener balance de cuenta {id}..."
            )
            try:
                response = requests.get(
                    url=f"{self.cobre_api_url}/v1/accounts/{id}", headers=headers
                )
                logger.debug(
                    f"Respuesta de la API - Status Code: {response.status_code}"
                )
                logger.debug(f"Respuesta de la API - Headers: {response.headers}")
                logger.debug(f"Respuesta de la API - Body: {response.text}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error en la petición HTTP: {str(e)}")
                return (
                    jsonify(
                        {"error": "Error de conexión con la API", "details": str(e)}
                    ),
                    500,
                )

            # Paso 4: Procesar la respuesta
            if response.status_code == 200:
                logger.info("Balance obtenido exitosamente")
                return (
                    jsonify(
                        {
                            "message": "Balance obtenido exitosamente",
                            "data": response.json(),
                        }
                    ),
                    200,
                )
            else:
                error_response = (
                    response.json()
                    if response.text
                    else {"message": "Error desconocido"}
                )
                logger.error(f"Error en la respuesta de la API: {error_response}")
                return (
                    jsonify(
                        {
                            "error": "Error al obtener el balance de la cuenta",
                            "details": error_response,
                            "status_code": response.status_code,
                        }
                    ),
                    response.status_code,
                )

        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return (
                jsonify({"error": "Error al procesar la solicitud", "details": str(e)}),
                500,
            )
