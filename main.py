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
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('0.2.3'))
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
    idioma = server_conf["idioma"]

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
    idioma = server_conf["idioma"]

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

#Atrapa todos los mensajes enviados
@bot.event
async def on_message(msg : discord.Message):
    if not msg.author.bot:
        if msg.content.startswith("p!"):
            await bot.process_commands(msg)
        else:
            server_id = str(msg.guild.id)
            member_id = str(msg.author.id)
            server_conf = Datos.getdata("servers/"+server_id+"/configs")
            idioma = server_conf["idioma"]

            if "canal_de_memes" in server_conf:
                if server_conf["canal_de_memes"] == str(msg.channel.id):
                    if msg.attachments:
                        pic_ext = ['.jpg','.png','.jpeg', '.gif', '.mp4', '.mp3', '.webp', '.mov']
                        arcnombre = msg.attachments[0].filename.lower()

                        for ext in pic_ext:
                            if arcnombre.endswith(ext):
                                await msg.add_reaction('👍')
                                await msg.add_reaction('👎')
                                break

            apto_sub = True
            if "palabras_prohibidas" in server_conf and not msg.author.guild_permissions.administrator:
                msj = msg.content.lower().split(" ")
                for palabra in server_conf["palabras_prohibidas"]:
                    try:
                        msj.index(palabra)

                        apto_sub = False
                        mensaje = idiomas.cell_value(43, idioma).replace("{palabra}", palabra)

                        adver = await msg.channel.send(f"{msg.author.mention} {mensaje}")
                        razon = f"Haber dicho ||{palabra}||\n**Mensaje:**\n{msg.content}"
                        fecha = datetime.today()

                        aviso = {
                            "por": "730804779021762561",
                            "razon": razon,
                            "fecha": fecha.strftime("%d/%m/%Y %H:%M"),
                            "cast_apl": {
                                "ddd": True
                            }
                        }

                        avisos = Datos.getdata("servers/"+server_id+"/miembros/"+member_id+"/avisos")

                        aviso_numero = 0
                        if avisos != None:
                            aviso_numero = len(avisos)
                        else:
                            Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/avisos", {"cast_apl": {"ddd":True}})

                        Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/avisos/"+aviso_numero, aviso)

                        if "canal_moderacion" in server_conf:
                            canal_moderacion = server_conf["canal_moderacion"]
                            try:
                                canal = bot.get_channel(int(canal_moderacion))
                                mod_embed = embeds.embed_moderador("<@!730804779021762561>", msg.author, razon, server_id, 47, idioma)

                                await canal.send(embed=mod_embed)
                            except discord.NotFound:
                                Datos.removedata("servers/"+server_id+"/configs/"+canal_moderacion)

                        avisos = Datos.getdata("servers/"+server_id+"/miembros/"+member_id+"/avisos")

                        if "castigos" in server_conf:
                            castigos_aplicar = []

                            for castigo in server_conf["castigos"]:
                                if castigo["cant_warns"] <= len(avisos):
                                    apl_castigo = True
                                    
                                    aviso_ver = avisos[str(len(avisos)-castigo["cant_warns"])]
                                    
                                    if str(castigo["id"]) in avisos["cast_apl"]:
                                        ult_cast_apl = datetime.strptime(avisos["cast_apl"][str(castigo["id"])], "%d/%m/%Y")
                                        fecha_ver = fecha - timedelta(server_conf["castigos_cooldown"])

                                        if (fecha_ver - ult_cast_apl.date()).days >= 0:
                                            if not str(castigo["id"]) in aviso_ver["cast_apl"]:
                                                fecha_ver = fecha - timedelta(castigo["en_dias"], (castigo["en_horas"]*60*60)+(castigo["en_minutos"]*60))
                                                fecha_ver2 = fecha_ver2 = datetime.strptime(aviso_ver["fecha"], "%d/%m/%Y %H:%M")
                                                tiempo = ((fecha_ver - fecha_ver2).days*24*60*60) + (fecha_ver - fecha_ver2).seconds

                                                if tiempo < 60:
                                                    castigos_aplicar.append(castigo)
                            
                            castigos_aplicar = sorted(castigos_aplicar, key = lambda i:(i["castigo"]), reversed=True)
                            if castigos_aplicar[0]["castigo"] > 1:
                                pass
                            else:
                                for castigo in castigos_aplicar:
                                    pass

                        try:
                            await msg.delete()
                        except discord.NotFound:
                            pass
                        break
                    except:
                        pass

            if database["servers"][server]["configs"]["niveles_de_habla"] and apto_sub:
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

"""for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        if filename != "FireBaseGestor.py" and filename != "embeds.py":"""
bot.load_extension(f'cogs.moderacion')

#Token del bot
#bot.run(getenv("DISCORD_SECRET_KEY"))
bot.run(getenv("prueba_bot"))