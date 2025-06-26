from flask import Flask
from dotenv import load_dotenv
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Controllers
from Controllers.auth_token_controller import cache

# Routes
from Routes.counter_party_router import counterPartyRoutes
from Routes.auth_token import authTokenRoutes
from Routes.cobre_balance_router import cobreBalanceRoutes
from Routes.debit_register_router import debitRegisterRoutes

app = Flask(__name__)
load_dotenv()

# Configuración del caché
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 3600

# Inicializar el caché con la aplicación Flask
cache.init_app(app)

# ruta para los routes
app.register_blueprint(counterPartyRoutes)
app.register_blueprint(cobreBalanceRoutes)
app.register_blueprint(debitRegisterRoutes)
# ruta para la autenticacion del token
app.register_blueprint(authTokenRoutes)

if __name__ == "__main__":
    app.run(debug=True)
