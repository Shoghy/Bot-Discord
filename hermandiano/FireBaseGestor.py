#Para que el programa no cree archivos temporales
import sys
sys.dont_write_bytecode = True

import firebase_admin as fire_ad
from firebase_admin import db
from os import getenv

class Bot_DB():
    
    def __init__(self):

        certificate = {
            "type": getenv('Fire_B_type'),
            "project_id": getenv('Fire_B_project_id'),
            "private_key_id": getenv('Fire_B_private_key_id'),
            "private_key": getenv('Fire_B_private_key'),
            "client_email": getenv('Fire_B_client_email'),
            "client_id": getenv('Fire_B_client_id'),
            "auth_uri": getenv('Fire_B_auth_uri'),
            "token_uri": getenv('Fire_B_token_uri'),
            "auth_provider_x509_cert_url": getenv('Fire_B_auth_provider_x509_cert_url'),
            "client_x509_cert_url": getenv('Fire_B_client_x509_cert_url')
        }

        firebase_sdk = fire_ad.credentials.Certificate(certificate)
        fire_ad.initialize_app(firebase_sdk, {"databaseURL":getenv("databaseURL")})
        self.db = db

    def get(self, path : str):
        resultado = self.db.reference(path)
        return resultado.get()

    def set_data(self, path : str, data):
        ref = self.db.reference(path)
        ref.set(data)

    def remove(self, path : str):
        datos = self.db.reference(path)
        datos.delete()

    def update(self, path : str, data):
        ref = self.db.reference(path)
        ref.update(data)

    def s_remove(self, path : str, indice : int):
        ref = self.db.reference(path)
        datos = ref.get()
        arr = []
        if isinstance(datos, dict):
            for i in datos:
                arr.append(datos[i])
        elif isinstance(datos, list):
            arr = datos
        
        del arr[indice]
        ref.set(arr)