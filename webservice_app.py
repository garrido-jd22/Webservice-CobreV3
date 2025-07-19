from flask import Flask
from dotenv import load_dotenv
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Controllers
from Controllers.auth_token_controller import cache

# Routes
from Routes.cobre_v3_router import cobreV3Routes
from Routes.counter_party_router import counterPartyRoutes
from Routes.auth_token import authTokenRoutes
from Routes.cobre_balance_router import cobreBalanceRoutes
from Routes.debit_register_router import debitRegisterRoutes
from Routes.money_movement_router import moneyMovementRoutes

app = Flask(__name__)
load_dotenv()

# Configuración del caché
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 3600

# Inicializar el caché con la aplicación Flask
cache.init_app(app)

# Cobre V3 APIs
app.register_blueprint(cobreV3Routes)
# ruta para los routes
app.register_blueprint(counterPartyRoutes)
app.register_blueprint(cobreBalanceRoutes)
app.register_blueprint(debitRegisterRoutes)
# ruta para la autenticacion del token
app.register_blueprint(authTokenRoutes)
# ruta para los movimientos de dinero
app.register_blueprint(moneyMovementRoutes)

if __name__ == "__main__":
    app.run(debug=True)
