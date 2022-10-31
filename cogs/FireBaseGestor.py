from firebase import firebase
from os import getenv
from dotenv import load_dotenv
from pathlib import Path
import sys
from asyncio import sleep

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
conexion = firebase.FirebaseApplication(getenv('data_base_url'), None)
sys.dont_write_bytecode = True

def getdata(path : str):
    resultado = conexion.get('', path)
    return resultado

def putdata(path : str, data):
    conexion.put('', path, data)

def deldata(path : str, data):
    conexion.delete(path, data)