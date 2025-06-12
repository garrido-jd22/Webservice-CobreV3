from flask import jsonify
from Database.database import Session
from Models.counter_party import CounterParty as CounterPartyModel
from Controllers.counter_party_controller import CounterParty as CounterPartyController

class ManagementFileController:
    # Constructor de la clase
    def __init__(self):
        self.session = Session()

    # Destructor de la clase
    def __del__(self):
        self.session.close()
        
    # Read File CSV
    def read_file_csv(self, file_path):
        try:
            return False
        except Exception as e:
            return jsonify({"message": f"Error reading file: {str(e)}"}), 500