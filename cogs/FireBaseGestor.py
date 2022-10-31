from firebase import firebase
from os import getenv
from dotenv import load_dotenv
from pathlib import Path
import sys

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
conexion = firebase.FirebaseApplication(getenv('data_base_url'), None)
sys.dont_write_bytecode = True

def alldata():
    resultado = conexion.get('', '/')
    return resultado

def new_server(server, data):
    conexion.put('', f'/servers/{server}', data)

def miembro(server, miembro, data):
    conexion.put('', f'/servers/{server}/miembros/{miembro}', data)

def mensaje(server, msg_id, data):
    conexion.put('', f'/servers/{server}/mensajes/{msg_id}', data)

def edit_configs(server, data):
    conexion.put('', f'/servers/{server}/configs', data)

def deldbmensaje(server, msg : str):
    conexion.delete(f'/servers/{server}/mensajes', msg)

def deldbserver(server):
    conexion.delete('/servers', server)

def deldbmiembro(server, miembro):
    conexion.delete(f'/servers/{server}/miembros', miembro)

def delconfig(server, config):
    conexion.delete(f'/servers/{server}/configs', config)