from flask import request, jsonify
from functools import wraps
from Controllers.auth_token_controller import Token as CobreToken


# Decorador para proteger rutas
def requieres_authentication(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token faltante o mal formado"}), 401

        token = auth_header.split(" ")[1]

        # Obtener el token válido desde CobreToken
        try:
            response = CobreToken.get_token()
            token_valido = response.get("token")
        except Exception as e:
            return jsonify({"error": f"Error interno al validar el token: {e}"}), 500

        if token != token_valido:
            return jsonify({"error": "Token inválido"}), 403

        return f(*args, **kwargs)
    return decorated
