from flask import Flask
from dotenv import load_dotenv
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Routes
from Routes.counter_parties_router import counterPartyRoutes
from Routes.auth_token import AuthTokenRoutes
from Controllers.auth_token_controller import cache

app = Flask(__name__)
load_dotenv()

# Configuración del caché
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 3600

# Inicializar el caché con la aplicación Flask
cache.init_app(app)

# ruta para los counter_parties
app.register_blueprint(counterPartyRoutes)
# ruta para la autenticacion del token
app.register_blueprint(AuthTokenRoutes)

if __name__ == "__main__":
    app.run(debug=True)
