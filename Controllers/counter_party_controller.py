import datetime
import logging
from flask import jsonify
from Database.database import Session
from Models.counter_party import CounterParty as CounterPartyModel

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
                        "type": counter.type,
                        "alias": counter.alias,
                        "metadata": {
                            "account_number": counter.account_number,
                            "counterparty_fullname": counter.counterparty_fullname,
                            "counterparty_id_type": counter.counterparty_id_type,
                            "counterparty_id_number": counter.counterparty_id_number,
                            "counterparty_phone": counter.counterparty_phone,
                            "counterparty_email": counter.counterparty_email,
                            # "registered_account": counter.registered_account, RELACION FK_COUNTERPARTY_ACCOUNT
                        },
                    }
                )
            return jsonify(counter_party_dict), 200
        else:
            return jsonify({"message": "Error al obtener las etapas"}), 500

    def get_counter_party(self, id_counter_party):
        counter_party_by_id = (
            self.session.query(CounterPartyModel)
            .filter(CounterPartyModel.id == id_counter_party)
            .first()
        )
        counter_party = {
            "id": counter_party_by_id.id,
            "geo": counter_party_by_id.geo,
            "type": counter_party_by_id.type,
            "alias": counter_party_by_id.alias,
            "metadata": {
                "account_number": counter_party_by_id.account_number,
                "counterparty_fullname": counter_party_by_id.counterparty_fullname,
                "counterparty_id_type": counter_party_by_id.counterparty_id_type,
                "counterparty_id_number": counter_party_by_id.counterparty_id_number,
                "counterparty_phone": counter_party_by_id.counterparty_phone,
                "counterparty_email": counter_party_by_id.counterparty_email,
            },
        }
        return jsonify(counter_party), 200

    def set_counter_party(self, datos_csv):

        self.session.add_all(datos_csv)
        self.session.commit()
        logger.debug("Registro de los debitos insertados correctamente")
        return jsonify({"message": "datos ingresados en la tabla correctamente."})

    def get_counter_party_by_id_load(self, id_data_load):

        counter_party_by_id_load = (
            self.session.query(CounterPartyModel)
            .filter(CounterPartyModel.fk_data_load == id_data_load)
            .all()
        )
        counter_party = []

        for cp in counter_party_by_id_load:
            counter_party.append(
                {
                    "id": cp.id,
                    "geo": cp.geo,
                    "type": cp.type,
                    "alias": cp.alias,
                    "metadata": {
                        "account_number": cp.account_number,
                        "reference_debit": cp.reference_debit,
                        "amount": cp.amount,
                        "counterparty_fullname": cp.counterparty_fullname,
                        "counterparty_id_type": cp.counterparty_id_type,
                        "counterparty_id_number": cp.counterparty_id_number,
                        "counterparty_phone": cp.counterparty_phone,
                        "counterparty_email": cp.counterparty_email,
                    },
                }
            )

        return jsonify(counter_party), 200

    def update_counter_party(self, id_counter_party):
        return id_counter_party
