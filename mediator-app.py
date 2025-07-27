from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Endpoint de Kuenta para obtener los clientes
KUENTA_AUTH_URL = "https://auth-api.kuenta.co"  # AUTH TOKEN
KUENTA_API_URL = "https://api.kuenta.co"  # API KUENTA

# Endpoints de acceso
ENDPOINTS = {
    "client_id": "da52086d-ac76-4b65-b2de-a1bf4dde57e2",
    "client_secret": "be19f1cedabef895202c14525ff420962952549015037b53eaf99abc0d39f2d2",
    "entity_id": "beafcbd8-bba7-4303-ad8d-cf33026717b3",
    "username": "horizonte-sas",
    "password": "2003",
}

# Endpoint de Bitrix para CRUD
BITRIX_API_URL = "https://api.bitrix.com/clientes" 

def fetch_kuenta_token():
    
    urltoken = f"{KUENTA_AUTH_URL}/v1/oauth/token"
    headers = {'Content-Type': 'application/json'}
    requestbody = {
        "grant_type": "client_credentials",
        "client_id": ENDPOINTS["client_id"],
        "client_secret": ENDPOINTS["client_secret"],
        "mfa_token": "",
        "refresh_token": "",
        "username": ENDPOINTS["username"],
        "password": ENDPOINTS["password"],
        "totp": ""
    }
    
    response = requests.post(urltoken, json=requestbody, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

def fetch_get_credits(token):
    urlgetcredits = f"{KUENTA_API_URL}/v1/receivables"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Config-Organization-ID': ENDPOINTS["entity_id"],
        'Organization-ID': ENDPOINTS["entity_id"],
    }
    
    response = requests.get(urlgetcredits, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# BITRIX CRUD
def fetch_get_etapas_bitrix(): 
    urlgetetapas = "https://horizontesas-fontumi.bitrix24.es/rest/6/yk2gkuji96q2nx2a/crm.dealcategory.stage.list.json"
    response = requests.get(urlgetetapas, json={"ID" : 24})
    return response.json()


# ROUTES
@app.route('/get-etapas-bitrix', methods=['GET'])
def get_etapas_bitrix():
    etapas = fetch_get_etapas_bitrix()
    
    if etapas:
        return jsonify(etapas), 200
    else:
        return jsonify({"message": "Error al obtener las etapas"}), 500
    
@app.route('/get-token-kuenta', methods=['GET'])
def get_token_kuenta():
    token = fetch_kuenta_token()
    
    if token:
        return jsonify(token), 200
    else:
        return jsonify({"message": "Error al obtener el token"}), 500

@app.route('/get-credits', methods=['GET'])
def get_credits():
    token = fetch_kuenta_token()
    
    kuenta_data = fetch_get_credits(token["access_token"])
    credit_body = []
    
    for item in kuenta_data["data"]["credits"]:
        credit_body.append(
            {
                "contact": {
                    # STUDENT
                    "student_firstName": item["debtorProfile"]["natural"]["firstName"],
                    "student_lastName": item["debtorProfile"]["natural"]["lastName"],
                    "stunent_id": item["keywords"]["idNumber"],
                    "student_name": item["keywords"]["name"],
                    "stunent_phone": item["keywords"]["phone"],
                    "student_email": item["debtorProfile"]["natural"]["email"],
                },
                "credit": {
                    # CREDIT
                    "credit_line": item["creditLine"]["name"],
                    "consecutive": item["consecutive"],
                }
            },
        )
    
    
    if kuenta_data:
        # return jsonify(kuenta_data), 200
        return jsonify(credit_body), 200
    else:
        return jsonify({"message": "Error al obtener los datos de Kuenta"}), 500


if __name__ == '__main__':
    app.run(debug=True)
