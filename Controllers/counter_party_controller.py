from flask import jsonify
from Database.database import Session
from Models.counter_party import CounterParty as CounterPartyModel
import json


class CounterParty:
    # Constructor de la clase
    def __init__(self):
        self.session = Session()

    # Destructor de la clase
    def __del__(self):
        self.session.close()

    # Get all counter parties
    def get_all_counter_party(self):
        counter_party = []
        counter_party = self.session.query(CounterPartyModel).all()

        if counter_party:
            counter_party_dict = []
            for counter in counter_party:
                counter_party_dict.append(
                    {
                        "id": counter.id,
                        "geo": counter.geo,
                        "type": counter.tipe,
                        "alias": counter.alias,
                        "metadata": {
                            "account_number": counter.account_number,
                            "counterparty_fullname": counter.counterparty_fullname,
                            "counterparty_id_type": counter.counterparty_id_type,
                            "counterparty_id_number": counter.counterparty_id_number,
                            "counterparty_phone": counter.counterparty_phone,
                            "counterparty_email": counter.counterparty_email,
                            "registered_account": counter.registered_account,
                        },
                    }
                )
            return jsonify(counter_party_dict), 200
        else:
            return jsonify({"message": "Error al obtener las etapas"}), 500

    def get_counter_party(self, id_counter_party):
        return False

    def set_counter_party(self, datos_csv):
        print(
            "data recibida dentro de la funcion para insertar en la db = ",
            datos_csv,
        )
        self.session.add_all(datos_csv)
        self.session.commit()
        print("datos ingresados en la tabla correctamente")
        return jsonify({"message": "datos ingresados en la tabla correctamente."})

    def update_counter_party(self, id_counter_party):
        return False
