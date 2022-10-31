from os import getenv
from dotenv import load_dotenv
from pathlib import Path

#Imports
import pyrebase

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

firebase_config = {
    "apiKey": getenv('f_apiKey'),
    "authDomain": getenv('f_authDomain'),
    "databaseURL": getenv('f_databaseURL'),
    "projectId": getenv('f_projectId'),
    "storageBucket": getenv('f_storageBucket'),
    "messagingSenderId": getenv('f_messagingSenderId'),
    "appId": getenv('f_appId'),
    "measurementId": getenv('f_measurementId')
}

firebase = pyrebase.initialize_app(firebase_config)

db = firebase.database()

def update_adddata(path : str, data):
    db.child(path).update(data)

def getdata(path : str):
    data = db.child(path).get().val()
    return data

def removedata(path : str):
    db.child(path).remove()