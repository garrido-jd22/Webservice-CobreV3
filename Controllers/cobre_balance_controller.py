from flask import jsonify
from Database.database import Session
import logging
from Models.cobre_balance import CobreBalance as CobreBalanceModel
from Models.cobre_balance import CobreAvailableServices as CobreAviableServicesModel

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CobreBalance:

    def __init__(self):
        self.session = Session()

    def __del__(self):
        self.session.close()

    def get_cobre_balance(self, id):
        cobre_balace_by_id = (
            self.session.query(CobreBalanceModel)
            .filter(CobreBalanceModel.id == id)
            .first()
        )
        cobre_aviable_service = (
            self.session.query(CobreAviableServicesModel)
            .filter(CobreAviableServicesModel.fk_cobre_balance == id)
            .all()
        )
        list_cobre_aviable_service = []
        
        for row in cobre_aviable_service:
            list_cobre_aviable_service.append(row.service_name)
        
        cobre_balance_account = {
            "id": cobre_balace_by_id.id,
            "provider_id": cobre_balace_by_id.provider_id,
            "provider_name": cobre_balace_by_id.provider_name,
            "connectivity": cobre_balace_by_id.connectivity,
            "alias": cobre_balace_by_id.alias,
            "metadata": {
                "available_services": list_cobre_aviable_service,
                "primary_account": cobre_balace_by_id.primary_account,
            },
            "account_number": cobre_balace_by_id.account_number,
            "account_type": cobre_balace_by_id.account_type,
            "obtained_balance": cobre_balace_by_id.obtained_balance,
            "obtained_balance_at": cobre_balace_by_id.obtained_balance_at,
            "geo": cobre_balace_by_id.geo,
            "currency": cobre_balace_by_id.currency,
            "created_at": (
                cobre_balace_by_id.created_at.isoformat()
                if cobre_balace_by_id.created_at
                else None
            ),
            "updated_at": (
                cobre_balace_by_id.updated_at.isoformat()
                if cobre_balace_by_id.updated_at
                else None
            ),
        }
        return jsonify(cobre_balance_account), 200
