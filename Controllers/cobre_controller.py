from flask_caching import Cache
import time
import requests

# Endpoint de Cobre para obtener los clientes
COBRE_AUTH_URL = "https://api.qa.cobre.co/v1/auth"  # AUTH TOKEN
COBRE_API_URL = "https://api.qa.cobre.co/v1/"  # API Cobre

# Endpoints de acceso
ENDPOINTS_COBRE = {"user_id": "cli_ooi706_tvaszw1njw", "secret": "wHHpz0;*gw4hvc"}

_cached_token = None
_token_expiration_time = 0

# Creamos una instancia de Cache (pero no la inicializamos aún)
cache = Cache()

# Inicializador que será llamado desde app.py
# def init_auth_cache(app):
#     app.config['CACHE_TYPE'] = 'SimpleCache'
#     app.config['CACHE_DEFAULT_TIMEOUT'] = 3600  # Valor por defecto si no se especifica
#     cache.init_app(app)

class Cobre:
    def get_cobre_token(self):
        global _cached_token, _token_expiration_time

        # Verifica si el token existe y si no ha expirado
        if _cached_token and time.time() < _token_expiration_time:
            print("Usando token en caché...")
            return _cached_token

        print("Obteniendo nuevo token de la API externa...")

        urltoken = f"{COBRE_API_URL}/auth"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        requestbody = ENDPOINTS_COBRE

        try:
            # Simula la llamada a tu API externa para obtener el token
            response = requests.post(urltoken, json=requestbody, headers=headers)

            response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
            token_data = response.json()
            
            _cached_token = token_data["access_token"]
            expiration_time = token_data["expiration_time"]  # Por defecto 1 hora si no se especifica
            
            _token_expiration_time = (
                time.time() + expiration_time - 60
            )  # Resta un margen para refrescar antes

            if not _cached_token:
                raise ValueError("No se pudo obtener el access_token de la respuesta.")

            return _cached_token
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener el token: {e}")
            _cached_token = None
            _token_expiration_time = 0
            raise  # Re-lanza la excepción para que el llamador la maneje
        except Exception as e:
            print(f"Error inesperado: {e}")
            _cached_token = None
            _token_expiration_time = 0
            raise

    def get_cache_token(self, token, expira_en_segundos=3600):
        cache.set("auth_token", token, timeout=expira_en_segundos)
        
    # Función para simular la invalidación del token (para pruebas)
    def invalidate_token(self):
        global _cached_token, _token_expiration_time
        _cached_token = None
        _token_expiration_time = 0
        print("Token invalidado.")
