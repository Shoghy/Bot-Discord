import requests
from dotenv import load_dotenv
from pathlib import Path
from os import getenv

#Obtener los datos del archivo .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Oauth(object):
    #Get guild_id
    #https://discord.com/api/oauth2/authorize?response_type=code&client_id=157730590492196864&scope=webhook.incoming&state=15773059ghq9183habn&redirect_uri=https%3A%2F%2Fnicememe.website
    client_id = "730804779021762561" #bot id
    scope= "identify guilds"
    redirect_url = "http://127.0.0.1:5000/login"
    discord_login_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_url}&response_type=code&scope={scope}"
    discord_token_url = "https://discord.com/api/oauth2/token"
    discord_api_url = "https://discord.com/api"

    @staticmethod
    def get_acces_token(code):
        data = {
            'client_id': Oauth.client_id,
            'client_secret': getenv("client_secret"),
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': Oauth.redirect_url,
            'scope': 'identify email connections'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        acceso = requests.post(url=Oauth.discord_token_url, data=data, headers=headers)
        return acceso.json()
    
    @staticmethod
    def get_guild_json(acces_token):
        url = Oauth.discord_api_url+'/users/@me/guilds'
        headers = {
            "Authorization": f"Bearer {acces_token}"
        }
        guilds = requests.get(url=url, headers=headers)
        return guilds.json()