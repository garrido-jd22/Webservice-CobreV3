from flask import jsonify
from Database.database import session_manager
from Models.counter_party import CounterParty as CounterPartyModel
import json
import requests
import logging
from Controllers.auth_token_controller import Token

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CounterParty:

    # Constructor de la clase
    def __init__(self):
        self.cobre_api_url = "https://api.qa.cobre.co"

    # Get all counter parties
    def get_all_counter_party(self):

        counter_party = []
        # counter_party = self.session.query(CounterPartyModel).all()

        if counter_party:
            counter_party_dict = []
            for counter in counter_party:
                counter_party_dict.append(
                    {
                        "id": counter.id,
                        "geo": counter.geo,
                        "type": counter.tipe,
                        "alias": counter.alias,
                        "metadata": {
                            "account_number": counter.account_number,
                            "counterparty_fullname": counter.counterparty_fullname,
                            "counterparty_id_type": counter.counterparty_id_type,
                            "counterparty_id_number": counter.counterparty_id_number,
                            "counterparty_phone": counter.counterparty_phone,
                            "counterparty_email": counter.counterparty_email,
                            "registered_account": counter.registered_account,
                        },
                    }
                )
            return jsonify(counter_party_dict), 200
        else:
            return jsonify({"message": "Error al obtener las etapas"}), 500

    def get_counter_party(self, id_counter_party):
        return False

    # insertar payload en la abse de datos
    def insert_database(self, cobre_payload: dict):
        """
        Guarda los datos en la base de datos de los counterparty a enviar por la API de Cobre
        en la base de datos local.
        """

        try:
            # Si los datos reales están anidados en una clave 'data', los extraemos.
            counterparty_data = cobre_payload.get("data", cobre_payload)

            logger.info("Insertando contraparte en la base de datos local...")
            metadata = counterparty_data.get("metadata", {})

            new_counter_party = CounterPartyModel(
                geo=counterparty_data.get("geo"),
                type=counterparty_data.get("type"),
                alias=counterparty_data.get("alias"),
                beneficiary_institution=metadata.get("beneficiary_institution"),
                account_number=metadata.get("account_number"),
                counterparty_fullname=metadata.get("counterparty_fullname"),
                counterparty_id_type=metadata.get("counterparty_id_type"),
                counterparty_id_number=metadata.get("counterparty_id_number"),
                counterparty_phone=metadata.get("counterparty_phone"),
                counterparty_email=metadata.get("counterparty_email"),
                registered_account=counterparty_data.get("registered_account", False),
            )

            with session_manager() as session:
                session.add(new_counter_party)
                session.commit()
                logger.info(
                    f"Contraparte con alias '{new_counter_party.alias}' guardada exitosamente en la BD."
                )
                return new_counter_party

        except Exception as e:
            logger.error(
                f"Error al insertar la contraparte en la base de datos: {str(e)}"
            )
            return None

    # ingresa un counterparty(cliente al que hay que hacerle el debito)
    def set_counter_party(self, data):
        """
        Método para crear un nuevo counter party en la API de Cobre

        Args:
            data (dict): Datos del counter party a crear

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
                    "geo": data.get("geo"),
                    "type": data.get("type"),
                    "alias": data.get("alias"),
                    "metadata": {
                        "counterparty_fullname": metadata.get("counterparty_fullname"),
                        "beneficiary_institution": metadata.get(
                            "beneficiary_institution"
                        ),
                        "account_number": metadata.get("account_number"),
                        "counterparty_id_type": metadata.get("counterparty_id_type"),
                        "counterparty_id_number": metadata.get(
                            "counterparty_id_number"
                        ),
                        "counterparty_phone": metadata.get("counterparty_phone"),
                        "counterparty_email": metadata.get("counterparty_email"),
                    },
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

            # Guardar en la base de datos local usando el payload para enviar a la api
            self.insert_database(payload_json)

            # Paso 4: Realizar la petición a la API
            logger.info("Enviando petición a la API...")
            try:
                response = requests.post(
                    url=f"{self.cobre_api_url}/v1/counterparties",
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
                logger.info("Counter party creado exitosamente en la API de Cobre.")
                cobre_payload = response.json()  # Payload de la API de Cobre

                # Guardar en la base de datos local usando los datos de respuesta de la api
                # self.insert_database(cobre_payload)

                return (
                    jsonify(
                        {
                            "message": "Counter party creado exitosamente",
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
                            "error": "Error al crear counter party en la API externa",
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

    def delete_counter_party(self, id_counter_party):
        return False
