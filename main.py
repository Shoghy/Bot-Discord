#Imports
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from requests import get
from io import BytesIO
from os import remove, listdir, getenv
import sys
from asyncio import sleep
from random import randint
from datetime import date
from threading import Thread
from xlrd import open_workbook as open_excel
from firebase import firebase
from dotenv import load_dotenv
from pathlib import Path
import cogs.FireBaseGestor as Datos

#Obtener los datos del archivo .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#Variables universales
client_secret = getenv('client_secret')
sys.dont_write_bytecode = True
idiomas = open_excel("cogs\\idiomas.xlsx")
idiomas = idiomas.sheet_by_name("bot")

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
def imgdni(avatar, nac, grupo_logo, name : str, id : int, nacionalidad : str = "Sin nacionalidad"):
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
    dni.save(str(id)+".png")

def pageweb():
    import WebPage.index

#Mensaje que se escribe cuando el bot ya está funcionando
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('0.2.1'))
    database = Datos.alldata()
    async for guild in bot.fetch_guilds(limit=None):
        if not str(guild.id) in database["servers"]:
            server = {}
            server["configs"] = {"idioma": 1, "niveles_de_habla":True, "cambiar_nombres":False}
            server["mensajes"] = {"ddf": True}
            server["miembros"] = {"ddf": True}
            Datos.new_server(str(guild.id), server)

    #Página web
    """t = Thread(target=pageweb)
    t.start()"""
    print("Estoy listo")

#Mensaje que se muestra cuando alguien nuevo entra al server
@bot.event
async def on_member_join(member):
    database = Datos.alldata()
    server = str(member.guild.id)
    if database["servers"][server]["configs"]["cambiar_nombres"]:
        if "palabras_prohibidas" in database["servers"][server]["configs"]:
            for palabra in database["servers"][server]["configs"]["palabras_prohibidas"]:
                palabra
                lugar_pal = member.name.find(palabra)
                if ((member.name[lugar_pal-1:len(palabra)+lugar_pal] == f" {palabra}"
                    and len(member.name) == len(palabra)+lugar_pal)
                    or (member.name[lugar_pal:len(palabra)+lugar_pal] == f"{palabra}"
                    and lugar_pal == 0
                    and len(member.name) == len(palabra)+lugar_pal)
                    or (member.name[lugar_pal:len(palabra)+lugar_pal+1] == f"{palabra} "
                    and lugar_pal == 0)
                    or member.name[lugar_pal-1:len(palabra)+lugar_pal+1] == f" {palabra} "):
                    nombres = ["Juan", "Nickname", "Gorfyx (Falso)", "(Nombre Generico)", "Hmmmm", "&@$#/°!*", "Nombre invalido", "Hola que hace",
                                "JPlkas", "Alastor", "NicoCore", "Deigamer", "Dedrevil", "Charmander", "Sospechoso", "Tengo nuevo nombre",
                                "Soy fan", "Nuevo Miembro", "Caballero", "Cebolinha", "Monica", "Cascão", "Magali", "Cosmo", "Timmy", "Wanda", "Tommy",
                                "Tomas", "Dora", "Botas", "Otaku", "Negas", "Pikachu", "Pablo", "Uniqua", "Tyrone", "Tasha", "Austin",
                                "Walter", "Garrafón", "Sans", "Hollow", "Mee6", "Pterodáctilo", "Ben 10", "Wendolyne", "Vilgax",
                                "Phineas", "Ferb", "Patricio", "Chavo", "Pueblerino", "Crash", "Ash", "Samus", "Zelda", "Link",
                                "Carlos", "Vegetta777", "Steve", "Fundy", "Dream", "Henry", "Finn", "Jake", "Mikecrack",
                                "Felps", "Cellbit", "A Cookie", "Isaac", "Robtop", "Alva", "Guinxu", "Toad", "Daarick", "Llama",
                                "Celendas", "Glados", "Fire Boy", "Water Girl", "Rubius", "Miguel", "Dipper", "Mabel", "Stan Lee",
                                "Hornet", "Pálido", "Metroid", "Yoshi", "Mario", "Peach", "Azucarilla", "Rick", "Morty", "Caboby",
                                "Buzz", "Lonrot", "Dama G", "Hey, Listen", "Quirrel", "Zote", "Yellow Guy", "Red Guy", "Duck", "ROY",
                                "Grimm", "Blue Baby", "Hush", "Chara", "Frisk", "Toriel", "SrPelo", "Max", "Dr.Flug", "Cyan",
                                "Jerry", "Gaster", "Grillby", "Guppy", "Ari", "Donald", "Lucas", "George", "Folagor", "Pascu",
                                "Rodri", "RichMC", "Conter"]
                    await member.edit(nick=nombres[randint(0, len(nombres)-1)])
                    break
    if "bienvenida_canal" in database["servers"][server]["configs"]:
        canal_bienvenida = int(database["servers"][server]["configs"]["bienvenida_canal"])
        mensaje = database["servers"][server]["configs"]["mensaje_bienvenida"]
        mensaje = mensaje.replace("{user}", f"{member.mention}")
        mensaje = mensaje.replace("{server}", f"**{member.guild.name}**")
        channel = bot.get_channel(canal_bienvenida)
        if "nacionalidad" in database["servers"][server]["configs"]:
            nacionalidad = database["servers"][server]["configs"]["nacionalidad"]
            imgdni(member.avatar_url, member.joined_at, member.guild.icon_url, member.display_name, member.id, nacionalidad)
        else:
            imgdni(member.avatar_url, member.joined_at, member.guild.icon_url, member.display_name, member.id)
        file = discord.File(str(member.id)+".png")
        await channel.send(mensaje, file=file)
        remove(str(member.id)+".png")
    if "nuevo_usuario_role" in database["servers"][server]["configs"]:
        role = int(database["servers"][server]["configs"]["nuevo_usuario_role"])
        try:
            roledeinicio = discord.utils.get(member.guild.roles, id=role)
            await member.add_roles(roledeinicio)
        except discord.NotFound:
            Datos.delconfig(server, "nuevo_usuario_role")

@bot.event
async def on_guild_join(guild):
    database = Datos.alldata()
    server = {}
    server["configs"] = {"idioma": 1, "niveles_de_habla": True, "cambiar_nombres":False}
    server["mensajes"] = {"ddf": True}
    server["miembros"] = {"ddf": True}
    Datos.new_server(str(guild.id), server)

@bot.event
async def on_guild_remove(guild):
    Datos.deldbserver(str(guild.id))

@bot.event
async def on_member_remove(member):
    database = Datos.alldata()
    server = str(member.guild.id)
    miembro = str(member.id)
    if "despedida_canal" in database["servers"][server]["configs"]:
        canal = database["servers"][server]["configs"]["despedida_canal"]
        mensaje = database["servers"][server]["configs"]["mensaje_despedida"]
        mensaje = mensaje.replace("{user}", f"**{member.display_name}**")
        if miembro in database["servers"][server]["miembros"]:
            Datos.deldbmiembro(server, miembro)
        try:
            channel = bot.get_channel(canal)
            despedida = await channel.send(mensaje)
            await despedida.add_reaction('👋')
        except:
            pass

#Comando que enseña el dni de un integrante
@bot.command(aliases=['cedula', 'documento', 'doc', 'cédula'])
async def dni(ctx, person : discord.Member = None):
    permisoconcedido = False
    database = Datos.alldata()
    server = str(ctx.message.guild.id)
    canal = str(ctx.channel.id)
    idioma = database["servers"][server]["configs"]["idioma"]
    if ctx.author.guild_permissions.administrator:
        permisoconcedido = True
    else:
        if "canal_comandos" in database["servers"][server]["configs"]:
            if canal in database["servers"][server]["configs"]["canal_comandos"]:
                permisoconcedido = True
    if permisoconcedido:
        if person == None:
            if "nacionalidad" in database["servers"][server]["configs"]:
                nacionalidad = database["servers"][server]["configs"]["nacionalidad"]
                imgdni(ctx.author.avatar_url, ctx.author.joined_at, ctx.guild.icon_url, ctx.author.name, ctx.author.id, nacionalidad)
            else:
                imgdni(ctx.author.avatar_url, ctx.author.joined_at, ctx.guild.icon_url, ctx.author.name, ctx.author.id)
            file = discord.File(str(ctx.author.id)+".png")
            await ctx.send(file=file)
            try:
                remove(str(ctx.author.id)+".png")
            except:
                pass
        else:
            if "nacionalidad" in database["servers"][server]["configs"]:
                nacionalidad = database["servers"][server]["configs"]["nacionalidad"]
                imgdni(person.avatar_url, person.joined_at, ctx.guild.icon_url, person.display_name, person.id, nacionalidad)
            else:
                imgdni(person.avatar_url, person.joined_at, ctx.guild.icon_url, person.display_name, person.id)
            file = discord.File(str(person.id)+".png")
            await ctx.send(file=file)
            try:
                remove(str(person.id)+".png")
            except:
                pass
    else:    
        if ctx.author.guild_permissions.administrator:
            if person == None:
                if "nacionalidad" in database["servers"][server]["configs"]:
                    nacionalidad = database["servers"][server]["configs"]["nacionalidad"]
                    imgdni(ctx.author.avatar_url, ctx.author.joined_at, ctx.guild.icon_url, ctx.author.name, ctx.author.id, nacionalidad)
                else:
                    imgdni(ctx.author.avatar_url, ctx.author.joined_at, ctx.guild.icon_url, ctx.author.name, ctx.author.id)
                file = discord.File(str(ctx.author.id)+".png")
                await ctx.send(file=file)
                try:
                    remove(str(ctx.author.id)+".png")
                except:
                    pass
            else:
                if "nacionalidad" in database["servers"][server]["configs"]:
                    nacionalidad = database["servers"][server]["configs"]["nacionalidad"]
                    imgdni(person.avatar_url, person.joined_at, ctx.guild.icon_url, person.display_name, person.id, nacionalidad)
                else:
                    imgdni(person.avatar_url, person.joined_at, ctx.guild.icon_url, person.display_name, person.id)
                file = discord.File(str(person.id)+".png")
                await ctx.send(file=file)
                try:
                    remove(str(person.id)+".png")
                except:
                    pass
        else:
            try:
                await ctx.message.delete()
            except discord.NotFound:
                pass
            no = await ctx.send(f'{ctx.author.mention}, {idiomas.cell_value(1, idioma)}')
            await sleep(3)
            try:
                await no.delete()
            except discord.NotFound:
                pass

#Comando para borrar mensajes
@bot.command(aliases=['borrar', 'purgar', 'msgkill', 'delete'])
async def clear(ctx, cant = None):
    permisoconcedido = False
    database = Datos.alldata()
    server = str(ctx.message.guild.id)
    idioma = database["servers"][server]["configs"]["idioma"]
    if ctx.author.guild_permissions.administrator:
        permisoconcedido = True
    else:
        if "roles_moderadores" in database["servers"][server]["configs"]:
            for role in ctx.author.roles:
                if str(role.id) in database["servers"][server]["configs"]["roles_moderadores"]:
                    permisoconcedido = True
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

#Atrapa todos los mensajes enviados
@bot.event
async def on_message(msg):
    if not msg.author.bot:
        await bot.process_commands(msg)
        database = Datos.alldata()
        server = str(msg.guild.id)
        if "canales_de_memes" in database["servers"][server]["configs"]:
            if database["servers"][server]["configs"]["canales_de_memes"] == msg.channel.id:
                if msg.attachments:
                    pic_ext = ['.jpg','.png','.jpeg', '.gif', '.mp4', '.mp3', '.webp', '.mov']
                    arcnombre = msg.attachments[0].filename.lower()
                    for ext in pic_ext:
                        if arcnombre.endswith(ext):
                            await msg.add_reaction('👍')
                            await msg.add_reaction('👎')
                            break
        if "palabras_prohibidas" in database["servers"][server]["configs"]:
            for palabra in database["servers"][server]["configs"]["palabras_prohibidas"]:
                msj = msg.content.lower()
                lugar_pal = msj.find(palabra)
                if lugar_pal > -1:
                    if ((msj[lugar_pal-1:len(palabra)+lugar_pal] == f" {palabra}"
                    and len(msj) == len(palabra)+lugar_pal)
                    or (msj[lugar_pal:len(palabra)+lugar_pal] == f"{palabra}"
                    and lugar_pal == 0
                    and len(msj) == len(palabra)+lugar_pal)
                    or (msj[lugar_pal:len(palabra)+lugar_pal+1] == f"{palabra} "
                    and lugar_pal == 0)
                    or msj[lugar_pal-1:len(palabra)+lugar_pal+1] == f" {palabra} "):
                        apto_sub = False
                        mensaje = idiomas.cell_value(43, database["servers"][server]["configs"]["idioma"]).replace("{palabra}", palabra)
                        try:
                            await msg.delete()
                        except discord.NotFound:
                            pass
                        await msg.channel.send(f"{msg.author.mention} {mensaje}")
                        break

        if database["servers"][server]["configs"]["niveles_de_habla"]:
            miembro = str(msg.author.id)

            if "canales_niveles" in database["servers"][server]["configs"]:
                canal_id = str(msg.channel.id)
                if canal_id in database["servers"][server]["configs"]["canales_niveles"]:
                    if database["servers"][server]["configs"]["canales_niveles"][canal_id]:
                        await nivel_social(miembro, database, server, msg.guild, msg.author)
                else:
                    if database["servers"][server]["configs"]["canales_niveles"]["allfalse"]:
                        await nivel_social(miembro, database, server, msg.guild, msg.author)
                    elif not database["servers"][server]["configs"]["canales_niveles"]["alltrue"]:
                        await nivel_social(miembro, database, server, msg.guild, msg.author)
            else:
                await nivel_social(miembro, database, server, msg.guild, msg.author)

async def nivel_social(miembro, database, server, guild, author):
    data = {}
    if not miembro in database["servers"][server]["miembros"]:
        data["nivel"] = 1
        data["xp"] = 1
        data["nxtniv"] = 100
    elif not "nivel" in database["servers"][server]["miembros"][miembro]:
        data = database["servers"][server]["miembros"][miembro]
        data["nivel"] = 1
        data["xp"] = 1
        data["nxtniv"] = 100
    else:
        data = database["servers"][server]["miembros"][miembro]
        xp = data["xp"]
        nxtniv = data["nxtniv"]
        if (xp+1) >= nxtniv:
            data["xp"] = 0
            nxtniv = int(nxtniv + (nxtniv * 0.5))
            data["nxtniv"] = nxtniv
            data["nivel"] += 1
            if "canal_fusn" in database["servers"][server]["configs"]:
                canal = guild.get_channel(int(database["servers"][server]["configs"]["canal_fusn"]["canal"]))
                if canal != None:
                    mensaje = str(database["servers"][server]["configs"]["canal_fusn"]["mensaje"])
                    mensaje = mensaje.replace("{user}", f"{author.mention}")
                    mensaje = mensaje.replace("{nivel}", f"{data['nivel']}")
                    await canal.send(mensaje)
            if "niv_roles" in database["servers"][server]["configs"]:
                if "n"+str(data["nivel"]) in database["servers"][server]["configs"]["niv_roles"]:
                    try:
                        role = discord.utils.get(guild.roles, id=int(database["servers"][server]["configs"]["niv_roles"]["n"+str(data["nivel"])]))
                        await author.add_roles(role)
                    except discord.NotFound:
                        print("Este mensaje")
                        pass
        else:
            data["xp"] += 1
    Datos.miembro(server, miembro, data)

#Mensaje de error
"""@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        print(error)"""
    #else:
        #await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Ocurrió un error:\n{error}')

for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        if filename != "FireBaseGestor.py":
            bot.load_extension(f'cogs.{filename[:-3]}')

#Token del bot
#bot.run(getenv("DISCORD_SECRET_KEY"))
bot.run(getenv("prueba_bot"))