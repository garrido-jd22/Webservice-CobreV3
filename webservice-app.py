from flask import Flask
from dotenv import load_dotenv

# Routes
from Routes.counter_party_router import counterPartyRoutes

app = Flask(__name__)
load_dotenv()

app.register_blueprint(counterPartyRoutes)

if __name__ == "__main__":
    app.run(debug=True)
