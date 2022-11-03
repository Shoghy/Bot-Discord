#No crear archivos temporales
import sys
sys.dont_write_bytecode = True

#Imports
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from io import BytesIO
from os import getenv
from xlrd import open_workbook as open_excel
from dotenv import load_dotenv
from pathlib import Path

#Obtener los datos del archivo .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

from hermandiano.FireBaseGestor import Bot_DB

#Variables universales
client_secret = getenv('client_secret')
exl = open_excel("hermandiano\\idiomas.xlsx")
bot_i = exl.sheet_by_name("bot")
Datos = Bot_DB()

#Lo que escucha el robot
intents = discord.Intents.none()
intents.members = True
intents.guild_reactions = True
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

#Prefix del bot
prefijo = "pr1"
#bot = commands.Bot(command_prefix='c!', intents=intents)
bot = commands.Bot(command_prefix=prefijo, intents=intents)

#Función que crea el dni
async def imgdni(avatar : discord.Asset, nac, grupo_logo : discord.Asset, name : str, id : int, nacionalidad):
    """Esta función crea una imagen, la cual guarda en un variable BytesIO.
    Dicha imagen es el DNI del usuario"""
    name_slited = ""
    if len(name) > 25: #Esto es por si el nombre del usuario es muy largo
        name_div = name.split()
        if len(name_div) > 1: #Si el nombre tiene más de 1 espacio en el
            if len(name_div[0]) < 25: #Si la primera palabra tiene menos de 25 letras
                nombre = ""
                nombre2 = ""
                n2 = True
                for m in name_div:
                    if len(nombre+m) < 25 and n2:
                        if nombre == "":
                            nombre = m
                        else:
                            nombre = nombre+" "+m

                    else:
                        n2 = False
                        if nombre2 == "":
                            nombre2 = m
                        else:
                            nombre2 = nombre2+" "+m

                name_slited = nombre+"\n"+nombre2
            else:
                name_slited = name[:25]+"\n"+name[25:]
        else:
            name_slited = name[:25]+"\n"+name[25:]
    else:
        name_slited = name

    dni = Image.open("DNI.png")
    avatarimg = None
    if avatar != None:
        avatarimg = Image.open(BytesIO(await avatar.read()))
    else:
        avatarimg = Image.open("default_img.png")

    if grupo_logo != None:
        grupo_img = Image.open(BytesIO(await grupo_logo.read()))
        grupo_img_lil = grupo_img.resize((130, 130))
        mask_grupo = Image.new("L", grupo_img_lil.size, 0)
        draw_grupo = ImageDraw.Draw(mask_grupo)
        draw_grupo.ellipse((10, 10, 120, 120), fill=255)
        mask_grupo_blur = mask_grupo.filter(ImageFilter.GaussianBlur(1))
        dni.paste(grupo_img_lil, (612, 370), mask_grupo_blur)
   
    avlittle = avatarimg.resize((250, 250))
    avatarimg.close()
    mask_im = Image.new("L", avlittle.size, 0)
    draw = ImageDraw.Draw(mask_im)
    draw.ellipse((10, 10, 240, 240), fill=255)
    mask_im_blur = mask_im.filter(ImageFilter.GaussianBlur(2))
    font = ImageFont.truetype("calibril.ttf", 24)
    font2 = ImageFont.truetype("calibril.ttf", 57)

    dni.paste(avlittle, (0, 0), mask_im_blur)
    draw = ImageDraw.Draw(dni)
    draw.text((405, 83), name_slited,(255,255,255),font=font)
    draw.text((463, 168), nacionalidad,(255,255,255),font=font)
    draw.text((446, 249), nac.strftime("%d")+"-"+nac.strftime("%m")+"-"+nac.strftime("%Y"),(255,255,255),font=font)
    draw.text((7, 443), str(id),(255,255,255),font=font2)
    with BytesIO() as img:
        dni.save(img, "PNG")
        dni.close()
        img.seek(0)
        file = discord.File(fp=img, filename="dni.png")
        return file

@bot.command()
async def refresh(ctx : commands.Context, cog : str):
    if ctx.author.id == 345737329383571459:
        print(f"Actualizando la extensión {cog}...")
        bot.reload_extension(f"cogs.{cog}")
        print(f"Extensión {cog} actualizada.")

from . import events
from .common import *
import moderacion

from . import slash_commands