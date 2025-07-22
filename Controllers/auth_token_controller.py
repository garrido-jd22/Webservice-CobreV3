from flask_caching import Cache
import time
import requests
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Endpoint de Cobre para obtener los clientes
COBRE_AUTH_URL = "https://api.cobre.co/v1/auth"  # AUTH TOKEN
COBRE_API_URL = "https://api.cobre.co/v1/"  # API Cobre

# Endpoints de acceso
# ENDPOINTS_COBRE_QA = {"user_id": "cli_ooi706_tvaszw1njw", "secret": "wHHpz0;*gw4hvc"}

# Configuración del caché
cache = Cache()


class Token:

    def __init__(self):
        try:
            logger.info("Inicializando clase Cobre")
        except Exception as e:
            logger.error(f"Error al inicializar la clase Cobre: {str(e)}")
            raise

    def get_token(self, requestbody):
        try:
            logger.info("Iniciando obtención de token")

            # Intentamos obtener el token desde el caché
            try:
                token_cached = cache.get("auth_token")
                token_expiration_time = cache.get("token_expiration")
            except Exception as e:
                logger.error(f"Error al obtener datos del caché: {str(e)}")
                token_cached = None
                token_expiration_time = None

            # Verificamos si el token existe y no ha expirado
            if (
                token_cached
                and token_expiration_time
                and time.time() < token_expiration_time
            ):
                logger.info("Token obtenido exitosamente desde caché")
                return {"token": token_cached, "expiration_time": token_expiration_time}

            logger.info("Obteniendo nuevo token de la API externa...")
            urltoken = f"{COBRE_API_URL}/auth"
            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            try:
                response = requests.post(urltoken, json=requestbody, headers=headers)
                response.raise_for_status()
                token_data = response.json()
                # logger.debug(f"### Respuesta de la API ###: \n {token_data} \n")

                if not token_data.get("access_token"):
                    raise ValueError(
                        "No se pudo obtener el access_token de la respuesta"
                    )

                # Calculamos el tiempo de expiración
                token_expiration_time = time.time() + 1200  # 1 hora desde ahora
                token = token_data["access_token"]

                # Guardamos el token y su tiempo de expiración en caché
                try:
                    self.set_cache_token(token, token_expiration_time)
                    logger.info(" ## Token guardado exitosamente en caché ## ")
                except Exception as e:
                    logger.error(f"Error al guardar en caché: {str(e)}")
                    # Continuamos aunque falle el caché

                return {"token": token, "expiration_time": token_expiration_time}

            except requests.exceptions.RequestException as e:
                logger.error(f"Error en la petición HTTP: {str(e)}")
                raise
            except ValueError as e:
                logger.error(f"Error en el formato de la respuesta: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Error inesperado en la petición: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Error general en get_cobre_token: {str(e)}")
            raise

    # funcion guardar token en la cache
    def set_cache_token(self, token, expiration_time):

        try:
            logger.info("Guardando token en caché")
            # Guardamos el token y su tiempo de expiración
            cache.set("auth_token", token, timeout=3600)  # 1 hora
            cache.set("token_expiration", expiration_time, timeout=3600)

            # Verificamos que se guardó correctamente
            stored_token = cache.get("auth_token")
            stored_expiration = cache.get("token_expiration")

            if not stored_token or not stored_expiration:
                raise ValueError("Error al verificar el almacenamiento en caché")

            logger.info("Token guardado exitosamente en caché")
            return True

        except Exception as e:
            logger.error(f"Error al guardar en caché: {str(e)}")
            raise

    # token invalidado o expirado
    def invalidate_token(self):
        try:
            logger.info("Invalidando token")
            cache.delete("auth_token")
            cache.delete("token_expiration")
            logger.info("Token invalidado exitosamente")
        except Exception as e:
            logger.error(f"Error al invalidar token: {str(e)}")
            raise
