#No crear archivos temporales
import sys
sys.dont_write_bytecode = True

#Imports
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from requests import get
from io import BytesIO
from os import remove, listdir, getenv
from asyncio import sleep
from random import randint
from datetime import date, timedelta, datetime
from threading import Thread
from xlrd import open_workbook as open_excel
from dotenv import load_dotenv
from pathlib import Path
import re
import cogs.FireBaseGestor as Datos
import cogs.embeds as embeds
import io

#Obtener los datos del archivo .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#Variables universales
client_secret = getenv('client_secret')
exl = open_excel("cogs\\idiomas.xlsx")
idiomas = exl.sheet_by_name("bot")

#Lo que escucha el robot
intents = discord.Intents.none()
intents.members = True
intents.guild_reactions = True
intents.guilds = True
intents.guild_messages = True

#Prefix del bot
#bot = commands.Bot(command_prefix='c!', intents=intents)
bot = commands.Bot(command_prefix='p!', intents=intents)

#Función que crea el dni
def imgdni(avatar, nac, grupo_logo, name : str, id : int, nacionalidad):
    if len(name) > 25:
        name_div = name.split()
        if len(name_div) > 1:
            if len(name_div[0]) < 25:
                nombre = ""
                nombre2 = ""
                for m in name_div:
                    if len(nombre+m) < 25:
                        if nombre == "":
                            nombre = m
                        else:
                            nombre = nombre+" "+m
                    else:
                        if nombre2 == "":
                            nombre2 = m
                        else:
                            nombre2 = nombre2+" "+m
                name = nombre+"\n"+nombre2
            else:
                name = name[:25]+"\n"+name[25:]
        else:
            name = name[:25]+"\n"+name[25:]

    dni = Image.open("DNI.png")
    url_img = get(avatar)
    avatarimg = Image.open(BytesIO(url_img.content))
    no_group_img = False

    try:
        url_img = get(grupo_logo)
    except:
        no_group_img = True

    if not no_group_img:
        grupo_img = Image.open(BytesIO(url_img.content))
        grupo_img_lil = grupo_img.resize((130, 130))
        mask_grupo = Image.new("L", grupo_img_lil.size, 0)
        draw_grupo = ImageDraw.Draw(mask_grupo)
        draw_grupo.ellipse((10, 10, 120, 120), fill=255)
        mask_grupo_blur = mask_grupo.filter(ImageFilter.GaussianBlur(1))
        dni.paste(grupo_img_lil, (612, 370), mask_grupo_blur)
   
    avlittle = avatarimg.resize((250, 250))
    mask_im = Image.new("L", avlittle.size, 0)
    draw = ImageDraw.Draw(mask_im)
    draw.ellipse((10, 10, 240, 240), fill=255)
    mask_im_blur = mask_im.filter(ImageFilter.GaussianBlur(2))
    font = ImageFont.truetype("calibril.ttf", 24)
    font2 = ImageFont.truetype("calibril.ttf", 57)

    dni.paste(avlittle, (0, 0), mask_im_blur)
    draw = ImageDraw.Draw(dni)
    draw.text((405, 83), name,(255,255,255),font=font)
    draw.text((463, 168), nacionalidad,(255,255,255),font=font)
    draw.text((446, 249), nac.strftime("%d")+"-"+nac.strftime("%m")+"-"+nac.strftime("%Y"),(255,255,255),font=font)
    draw.text((7, 443), str(id),(255,255,255),font=font2)
    with io.BytesIO() as img:
        dni.save(img, "PNG")
        img.seek(0)
        file = discord.File(fp=img, filename="dni.png")
        return file

def pageweb():
    import WebPage.index

#Mensaje que se escribe cuando el bot ya está funcionando
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('0.2.4'))
    servers = Datos.getdata('servers')
    async for guild in bot.fetch_guilds(limit=None):
        if not str(guild.id) in servers:
            Datos.update_adddata("servers/"+str(guild.id), servers["default"])

    #Página web
    """t = Thread(target=pageweb)
    t.start()"""

    print("Estoy listo")

#Mensaje que se muestra cuando alguien nuevo entra al server
@bot.event
async def on_member_join(member):
    server_id = str(member.guild.id)
    server_conf = Datos.getdata("servers/"+server_id+"/configs")

    if server_conf["cambiar_nombres"]:
        if "palabras_prohibidas" in server_conf:
            nombre_mem = member.name.split(" ")

            for palabra in server_conf["palabras_prohibidas"]:
                try:
                    nombre_mem.index(palabra)
                    nombres = exl.sheet_by_name("nombres")
                    await member.edit(nick=nombres.cell_value(randint(0, 70), 0))
                except:
                    pass
                #analizador = r"(^|\s)"+ re.escape(palabra) + r"($|\s)

    if "canal_bienvenida" in server_conf:
        canal_b_id = int(server_conf["canal_bienvenida"]["canal"])
        canal_b = bot.get_channel(canal_b_id)

        mensaje_b = server_conf["canal_bienvenida"]["mensaje"]
        mensaje_b = mensaje_b.replace("{user}", f"{member.mention}")
        mensaje_b = mensaje_b.replace("{server}", f"{member.guild.name}")

        nacionalidad = "Sin nacionalidad"
        if "nacionalidad" in server_conf:
            nacionalidad = server_conf["nacionalidad"]

        file = imgdni(member.avatar_url, member.joined_at, member.guild.icon_url, member.display_name, member.id, nacionalidad)
        await canal_b.send(mensaje_b, file=file)

    if "nuevo_miembro_role" in server_conf:
        role_newmem_id = int(server_conf["nuevo_miembro_role"])

        try:
            role_newmem = discord.utils.get(member.guild.roles, id=role_newmem_id)
            await member.add_roles(role_newmem)
        except discord.NotFound:
            Datos.removedata("servers/"+server_id+"/configs/nuevo_miembro_role")

@bot.event
async def on_guild_join(guild):
    server = Datos.getdata("servers/default")
    Datos.update_adddata("servers/"+str(guild.id), server)

@bot.event
async def on_guild_remove(guild):
    Datos.removedata("servers/"+str(guild.id))

@bot.event
async def on_member_remove(member):
    server_id = str(member.guild.id)
    server_data = Datos.getdata("servers/"+server_id)
    miembro_id = str(member.id)

    if "canal_despedida" in server_data["configs"]:
        canal_d_id = server_data["configs"]["canal_despedida"]["canal"]
        mensaje_d = server_data["configs"]["canal_despedida"]["mensaje"]
        mensaje_d = mensaje_d.replace("{user}", f"{member.display_name}")

        if miembro_id in server_data["miembros"]:
            Datos.removedata("servers/"+server_id+"/miembros/"+miembro_id)

        try:
            channel = bot.get_channel(canal_d_id)
            despedida = await channel.send(mensaje_d)
            await despedida.add_reaction('👋')
        except:
            pass

#Comando que enseña el dni de un integrante
@bot.command(aliases=['cedula', 'documento', 'doc', 'cédula'])
async def dni(ctx, person : discord.Member = None):
    server_id = str(ctx.message.guild.id)
    server_conf = Datos.getdata("servers/"+server_id+"/configs")
    canal_id = str(ctx.channel.id)
    idioma = server_conf["idioma"]+1

    permisoconcedido = False
    if ctx.author.guild_permissions.administrator:
        permisoconcedido = True
    else:
        if "canales_comandos_simples" in server_conf:
            if canal_id in server_conf["canales_comandos_simples"]:
                permisoconcedido = True
        else:
            permisoconcedido = True

    if permisoconcedido:
        nacionalidad = "Sin nacionalidad"
        if "nacionalidad" in server_conf:
            nacionalidad = server_conf["nacionalidad"]

        if person == None:
            file = imgdni(ctx.author.avatar_url, ctx.author.joined_at, ctx.guild.icon_url, ctx.author.name, ctx.author.id, nacionalidad)
            await ctx.send(file=file)

        else:
            file = imgdni(person.avatar_url, person.joined_at, ctx.guild.icon_url, person.display_name, person.id, nacionalidad)
            await ctx.send(file=file)

#Comando para borrar mensajes
@bot.command(aliases=['borrar', 'msgkill', 'delete'])
async def clear(ctx, cant = None):
    server_id = str(ctx.message.guild.id)
    server_conf = Datos.getdata("servers/"+server_id+"/configs")
    idioma = server_conf["idioma"]+1

    permisoconcedido = False
    if ctx.author.guild_permissions.administrator:
        permisoconcedido = True
    else:
        if "roles_moderador" in server_conf:
            for role in ctx.author.roles:
                try:
                    server_conf["roles_moderador"].index(str(role.id))
                    permisoconcedido = True
                    break
                except:
                    pass

    if permisoconcedido:
        try:
            cant = int(cant)
            if cant <= 0:
                cant = str("no")
        except:
            cant = str("no")

        if cant != None and isinstance(cant, int):
            if cant <= 300:
                if not ctx.message.mentions:
                    async for message in ctx.channel.history(limit=cant+1):
                        try:
                            await message.delete()
                        except discord.NotFound:
                            pass
                else:
                    deletedmsg = 0
                    await ctx.message.delete()
                    async for message in ctx.channel.history(limit=None):
                        if message.author.id == ctx.message.mentions[0].id:
                            try:
                                await message.delete()
                            except discord.NotFound:
                                pass
                            deletedmsg += 1
                        if deletedmsg >= cant:
                            break

                if cant != 1:
                    msg = idiomas.cell_value(3, idioma)
                    msg = msg.replace("{cant}", f"{cant}")
                    listo = await ctx.send(msg)
                    await sleep(3)
                    try:
                        await listo.delete()
                    except discord.NotFound:
                        pass

                else:
                    msg = idiomas.cell_value(2, idioma)
                    listo = await ctx.send(msg)
                    await sleep(3)
                    try:
                        await listo.delete()
                    except discord.NotFound:
                        pass

            else:
                msg = idiomas.cell_value(28, idioma)
                er = await ctx.send(f'{ctx.author.mention} {msg}')
                await sleep(3)
                try:
                    await er.delete()
                except discord.NotFound:
                    pass
        else:
            msg = idiomas.cell_value(4, idioma)
            er = await ctx.send(f'{ctx.author.mention} {msg}')
            await sleep(3)
            try:
                await er.delete()
            except discord.NotFound:
                pass
    else:
        msg = idiomas.cell_value(5, idioma)
        adver = await ctx.send(f'{ctx.author.mention} {msg}')
        await sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass

#Mensaje de error
"""@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        print(error)"""
    #else:
        #await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Ocurrió un error:\n{error}')

"""for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        if filename != "FireBaseGestor.py" and filename != "embeds.py":
bot.load_extension(f'cogs.moderacion')"""

#Token del bot
#bot.run(getenv("DISCORD_SECRET_KEY"))
bot.run(getenv("prueba_bot"))