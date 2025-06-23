from flask import Blueprint, request
from Controllers.debit_register_controller import debit_register

debitRegisterRoutes = Blueprint("debit_register", __name__)


@debitRegisterRoutes.route("/debitRegister", methods=["POST"])
def create_debit_register():
    try:
        data_registerdebit = request.get_json()

        # Instanciamos el nuevo controlador y llamamos al método correcto

        result = debit_register().set_direct_debit()

        return result

    except Exception as e:
        return {"error": "Error al procesar la solicitud", "details": str(e)}, 500
