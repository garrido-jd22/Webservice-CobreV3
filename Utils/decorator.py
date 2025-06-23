from flask import Flask, request, jsonify
from functools import wraps

# Token válido (en la vida real, esto vendría de un login u otro sistema)
TOKEN_VALIDO = "mi-token-secreto"

# Decorador para proteger rutas
def requiere_autenticacion(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token faltante o mal formado"}), 401

        token = auth_header.split(" ")[1]
        if token != TOKEN_VALIDO:
            return jsonify({"error": "Token inválido"}), 403

        return f(*args, **kwargs)
    return decorated

# Ruta protegida
# @app.route("/api/datos", methods=["GET"])
# @requiere_autenticacion
# def obtener_datos():
#     return jsonify({"mensaje": "Datos accedidos correctamente con token"}), 200
