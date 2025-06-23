from flask import jsonify
from Database.database import session_manager
from Models.direct_debit_registration import (
    DirectDebitRegistration,
    DebitMetadata,
    DebitStatus,
)
import json
import requests
import logging
from Controllers.auth_token_controller import Token

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class debit_register:

    # Constructor de la clase
    def __init__(self):

        # url_completa = "https://api.qa.cobre.co/v1/counterparties/{counterparty_id}/direct_debit_registrations"

        # la direccion necesita el counterparty ya existente el cual debe provenir del endpoint para usar el servicio de crear un direct debit
        self.register_debit_api_url = "https://api.qa.cobre.co/v1/counterparties"

        # se necesita obtener un counterparty existente y el que se va usar en los metodos del debit restritation

    # insertar payload en la base de datos local
    def insert_database(self, register_payload: dict):
        """
        Método para guardar en la base de datos local
        """

        try:
            # Si los datos reales están anidados en una clave 'data', los extraemos.
            direct_debit_data = register_payload.get("data", register_payload)

            logger.info("Insertando contraparte en la base de datos local...")
            metadata = direct_debit_data.get("metadata", {})

            new_direct_debit = DirectDebitRegistration()

            with session_manager() as session:
                session.add(new_direct_debit)
                session.commit()
                logger.info(
                    f"Contraparte con alias '{new_direct_debit.registration_description}' guardada exitosamente en la BD."
                )
                return new_direct_debit

        except Exception as e:
            logger.error(
                f"Error al insertar la contraparte en la base de datos: {str(e)}"
            )
            return None

    # -----------------------------------------------------------------------------------------

    # ingresa un direct debit, realizar un registro previo a la entidad bancaria relacionando la cuenta del counter party y la cuenta cobre balance
    def set_direct_debit(self, data: dict):
        """
        Método para crear un nuevo registro direct debit a un counterparty(cliente) en la API de Cobre

        Args:
            data (dict): Datos del direct debit a crear

        Returns:
            tuple: (response_json, status_code)
        """
        try:
            # Paso 1: Obtener token de autenticación
            logger.info("Obteniendo token de autenticación...")
            # cobre = Cobre()
            token_data = Token.get_token()
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

            logger.info(
                "data counter party que viene de la creacion del counterparty", data
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
                destination = data.get("destination", {})

                # agregar y Asegurar de que los datos estén en el formato correcto
                payload = {}

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

            counterparty_id = data["id"]

            # Guardar en la base de datos local usando el payload para enviar a la api
            self.insert_database(payload_json)

            # Paso 4: Realizar la petición a la API
            logger.info("Enviando petición a la API...")
            try:
                response = requests.post(
                    url=f"{self.register_debit_api_url}/{counterparty_id}/direct_debit_registrations",
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
                logger.info("direct debit creado exitosamente en la API de Cobre.")
                cobre_payload = response.json()  # Payload de la API de Cobre

                # Guardar en la base de datos local usando los datos de respuesta de la api
                # self.insert_database(cobre_payload)

                return (
                    jsonify(
                        {
                            "message": "direct debit creado exitosamente",
                            "data": cobre_payload,
                        }
                    ),
                    response.status_code,  # Usamos el status code de la respuesta original
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
                            "error": "Error al crear direct debit en la API externa",
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

    # este metodo se tiene que ejecutar  despues de 24 hora, el proceso del registro es un tiempo que nos dan para que se complete el proceso
    def get_confirmation_register():
        return False
