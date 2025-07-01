import logging
from Controllers.auth_token_controller import Token as CobreToken 

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CobreV3:

    BASE_URL = "https://api.cobre.co/v1"

    def __init__(self):
        self.token = self.obtener_token()
    def obtener_token(self):
        try:
            response = CobreToken.get_token()
            if response.get("status") == "success":
                return response["data"]["token"]
            else:
                logging.error("Error al obtener token de Cobre: respuesta inválida")
                return None
        except Exception as e:
            logging.error(f"Excepción al obtener token de Cobre: {e}")
            return None
