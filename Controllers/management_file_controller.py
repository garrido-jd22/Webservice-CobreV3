from flask import jsonify
from Database.database import Session
from Models.counter_party import CounterParty as CounterPartyModel
from Controllers.counter_party_controller import CounterParty as CounterPartyController
import csv
from datetime import datetime
import json


class ManagementFileController:
    # Constructor de la clase
    def __init__(self):
        self.session = Session()

    # Destructor de la clase
    def __del__(self):
        self.session.close()

    # funcion leer archivo c.vs
    def read_file_csv(self, file_path):
        try:
            counter_parties = []
            # Abre el archivo CSV en modo lectura
            with open(
                file_path, mode="r", newline="", encoding="utf-8-sig"
            ) as archivo_csv:

                # Usa csv.DictReader para leer el archivo como diccionarios (cada fila es un diccionario)
                lector_csv = csv.DictReader(archivo_csv)

                # Convertir DictReader a lista de diccionarios
                datos_csv = list(lector_csv)

                print("Datos del CSV:")
                print(datos_csv)
                print("---------------")

                counter_parties = []

                for fila in datos_csv:
                    #     Crear una instancia del modelo CounterParty,Para cada fila del CSV:
                    #     Mapea los datos del CSV obtenidos al a leer el archivo a los campos del modelo

                    counter_party = CounterPartyModel(
                        # en el get el primer valor seria el titulo de una columna del archivo csv, el segundo valor es por defecto, se setea para debuggear si no se encuentra
                        geo=fila["geo"],
                        tipe=fila["tipe"],
                        alias=fila["alias"],
                        beneficiary_institution=int(fila["beneficiary_institution"]),
                        account_number=fila["account_number"],
                        counterparty_fullname=fila["counterparty_fullname"],
                        counterparty_id_type=fila["counterparty_id_type"],
                        counterparty_id_number=fila["counterparty_id_number"],
                        counterparty_phone=fila["counterparty_phone"],
                        counterparty_email=fila["counterparty_email"],
                        registered_account=False,
                        fecha_reg=datetime.now(),
                    )

                    # Almacena todos los diccionarios en una lista
                    counter_parties.append(counter_party)

                CounterPartyController.set_counter_party(self, counter_parties)

            return (
                jsonify(
                    {
                        "message": "Archivo procesado exitosamente",
                        "data": datos_csv,
                    }
                ),
                200,
            )

        except FileNotFoundError:
            return (
                jsonify({"error": f"El archivo '{file_path}' no fue encontrado."}),
                404,
            )
        except Exception as e:
            return jsonify({"error": f"Error procesando el archivo: {str(e)}"}), 500
