from flask import jsonify
import datetime
from Database.database import Session
from Models.data_load import DataLoad as DataLoadModel


class DataLoad:
    # Constructor de la clase
    def __init__(self):
        self.session = Session()

    # Destructor de la clase
    def __del__(self):
        self.session.close()

    def set_data_load(self, id_data_load, state):
        try:
            data_load = DataLoadModel(
                id=id_data_load, state=state, created_at=datetime.datetime.now()
            )
            self.session.add(data_load)
            self.session.commit()
            return jsonify({"message": "Data load registered successfully"}), 201
        except Exception as e:
            self.session.rollback()
            return jsonify({"message": f"Error registering data load: {str(e)}"}), 500
