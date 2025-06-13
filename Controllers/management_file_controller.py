from flask import jsonify
from Database.database import Session
from Models.counter_party import CounterParty as CounterPartyModel
from Controllers.counter_party_controller import CounterParty as CounterPartyController
import csv
from datetime import datetime

class ManagementFileController:
    # Constructor de la clase
    def __init__(self):
        self.session = Session()

    # Destructor de la clase
    def __del__(self):
        self.session.close()
        
    #funcion leer archivo c.vs
    def read_file_csv(self, file_path):
        try:
            counter_parties = []
            #Abre el archivo CSV en modo lectura
            with open(file_path, mode='r', newline='', encoding='utf-8') as archivo_csv:
                
                #Usa csv.DictReader para leer el archivo como diccionarios (cada fila es un diccionario)
                lector_csv = csv.DictReader(archivo_csv)
                
                for fila in lector_csv:
                    # Crear una instancia del modelo CounterParty,Para cada fila del CSV:
                    #Mapea los datos del CSV a los campos del modelo
                    #Convierte los tipos de datos según sea necesario (ej: string a int para beneficiary_institution)
                    #Convierte el booleano registered_account de string a boolean
                    counter_party = CounterPartyModel(
                        #en el get el primer valor seria el titulo de una columna del archivo csv, el segundo valor es por defecto, se setea para debuggear si no se encuentra
                        geo=fila.get('geo', 'col'),
                        tipe=fila.get('tipe', 'xxx'),
                        alias=fila.get('alias', 'ger'),
                        beneficiary_institution=int(fila.get('beneficiary_institution', 0)),
                        account_number=fila.get('account_number', '457854248'),
                        counterparty_fullname=fila.get('counterparty_fullname', 'german garmendia'),
                        counterparty_id_type=fila.get('counterparty_id_type', 'cc'),
                        counterparty_id_number=fila.get('counterparty_id_number', '10022124578'),
                        counterparty_phone=fila.get('counterparty_phone', '3001245754'),
                        counterparty_email=fila.get('counterparty_email', 'german@gmail.com'),
                        registered_account=fila.get('registered_account', '').lower() == 'true',
                        fecha_reg=datetime.now()
                    )
                    
                    # Convertir a diccionario usando el método to_dict
                    # Almacena todos los diccionarios en una lista
                    counter_parties.append(counter_party.to_dict())
            #Devuelve un JSON con la lista de datos procesados
            return jsonify({
                "message": "Archivo procesado exitosamente",
                "data": counter_parties
            }), 200
                    
        except FileNotFoundError:
            return jsonify({"error": f"El archivo '{file_path}' no fue encontrado."}), 404
        except Exception as e:
            return jsonify({"error": f"Error procesando el archivo: {str(e)}"}), 500