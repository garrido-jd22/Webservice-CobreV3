from datetime import datetime
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

    # Get all counter parties
    def get_all_counter_party(self):
        counter_party = []
        counter_party = self.session.query(CounterPartyModel).all()

        if counter_party:
            counter_party_dict = []
            for counter in counter_party:
                counter_party_dict.append(
                    {
                        # "id": counter.id,
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
                            "beneficiary_institution": counter.beneficiary_institution,
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
                "beneficiary_institution": counter_party_by_id.beneficiary_institution,
            },
        }
        return jsonify(counter_party), 200

    def set_counter_party(self, counter_parties_saved, id_data_load):

        counter_parties = []

        for row in counter_parties_saved:
            counter_parties.append(
                CounterPartyModel(
                    id=row["id"],
                    fk_data_load=id_data_load,
                    geo=row["geo"],
                    type=row["type"],
                    alias=row["alias"],
                    beneficiary_institution=row["beneficiary_institution"],
                    account_number=row["account_number"],
                    counterparty_fullname=row["counterparty_fullname"],
                    counterparty_id_type=row["counterparty_id_type"],
                    counterparty_id_number=row["counterparty_id_number"],
                    counterparty_phone=row["counterparty_phone"],
                    counterparty_email=row["counterparty_email"],
                    fecha_reg=datetime.now(),
                )
            )

        self.session.add_all(counter_parties)
        self.session.commit()
        logger.debug("Registro de los debitos insertados correctamente")
        return jsonify({"message": "datos ingresados en la tabla correctamente."})

    def set_counter_party_cobre_body(self, counter_parties_saved, id_data_load):
        counter_parties = []

        for row in counter_parties_saved:
            counter_parties.append(
                CounterPartyModel(
                    id=row["id"],
                    fk_data_load=id_data_load,
                    geo=row["geo"],
                    type=row["type"],
                    alias=row["alias"],
                    beneficiary_institution=row["metadata"]["beneficiary_institution"],
                    account_number=row["metadata"]["account_number"],
                    counterparty_fullname=row["metadata"]["counterparty_fullname"],
                    counterparty_id_type=row["metadata"]["counterparty_id_type"],
                    counterparty_id_number=row["metadata"]["counterparty_id_number"],
                    counterparty_phone=row["metadata"]["counterparty_phone"],
                    counterparty_email=row["metadata"]["counterparty_email"],
                    fecha_reg=datetime.now(),
                )
            )

        self.session.add_all(counter_parties)
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
                        "counterparty_fullname": cp.counterparty_fullname,
                        "counterparty_id_type": cp.counterparty_id_type,
                        "counterparty_id_number": cp.counterparty_id_number,
                        "counterparty_phone": cp.counterparty_phone,
                        "counterparty_email": cp.counterparty_email,
                        "beneficiary_institution": cp.beneficiary_institution,
                    },
                }
            )

        return jsonify(counter_party), 200

    def get_counter_party_code(
        self, counterparty_id_number, beneficiary_institution, id_data_load
    ):

        counter_party_by_id_load = (
            self.session.query(CounterPartyModel)
            .filter(
                CounterPartyModel.counterparty_id_number == counterparty_id_number,
                CounterPartyModel.beneficiary_institution == beneficiary_institution,
                CounterPartyModel.fk_data_load == id_data_load,
            )
            .first()
        )
        counter_party_id = counter_party_by_id_load.id

        return counter_party_id

    def update_counter_party(self, id_counter_party):
        return id_counter_party
