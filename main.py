#No crear archivos temporales
import sys
sys.dont_write_bytecode = True

#Imports
from typing import Union
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from io import BytesIO
from os import listdir, getenv
from asyncio import sleep
from random import randint
from threading import Thread
from xlrd import open_workbook as open_excel
from dotenv import load_dotenv
from pathlib import Path
from cogs.FireBaseGestor import Bot_DB
from discord import option

#Obtener los datos del archivo .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#Variables universales
client_secret = getenv('client_secret')
exl = open_excel("cogs\\idiomas.xlsx")
idiomas = exl.sheet_by_name("bot")
Datos = Bot_DB()

#Lo que escucha el robot
intents = discord.Intents.none()
intents.members = True
intents.guild_reactions = True
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

#Prefix del bot
prefijo = "prueba"
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
    avatarimg = Image.open(BytesIO(await avatar.read()))

    if grupo_logo != None:
        grupo_img = Image.open(BytesIO(await grupo_logo.read()))
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

def pageweb():
    import WebPage.index

#Esta función se ejecuta una vez que el bot ya está listo para ser usado
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('0.2.8'))
    servers_id = Datos.get("servers list")
    def_server = Datos.get("servers/def_n_server")
    async for guild in bot.fetch_guilds(limit=None):
        if not str(guild.id) in servers_id:
            Datos.update("servers list", {str(guild.id): 0})
            Datos.update("servers", {str(guild.id): def_server})
            print(f"He añadido el servidor: {guild.id} a la lista de servidores.")

    #Página web
    """t = Thread(target=pageweb)
    t.start()"""
    print("Estoy listo")

#Esta función se ejecuta cada vez que un miembro entra a un server
#Le da la bienvenida y les pone un rol (Si esas funciones están configuradas)
@bot.event
async def on_member_join(member : discord.Member):
    server_id = str(member.guild.id)
    server_conf = Datos.get("servers/"+server_id+"/configs")
    
    #Si el nombre del usuario contiene una palabra prohibida en su nombre, el bot puede cambiar su apodo
    if "cambiar_nombres" in server_conf:
        palabras_prohibidas = Datos.get("servers/"+server_id+"/moderacion/palabras_prohibidas")
        if palabras_prohibidas != False:
            nombre_mem = member.name.split(" ")

            for palabra in palabras_prohibidas:
                #analizador = r"(^|\s)"+ re.escape(palabra) + r"($|\s)
                if palabra in nombre_mem:
                    nombres = exl.sheet_by_name("nombres")
                    await member.edit(nick=nombres.cell_value(randint(0, 62), 0))

    #Le da la bienvenida al usuario en caso de que el servidor tenga un mensaje de bienvenida
    if "bienvenida" in server_conf:
        bienvenida = server_conf["bienvenida"]
        canal_b_id = int(bienvenida["canal"])
        
        #Intenta acceder al canal de bienvenidas
        #En caso de no lograr acceder al canal, el valor de canal_b será None
        try:
            canal_b = bot.get_channel(canal_b_id)
        except (discord.HTTPException, discord.NotFound):
            canal_b = None
        except:
            canal_b = None
            print("Error no reconocido al intentar obtener canal de bienvenida\nDatos del error:")
            for info in sys.exc_info():
                print(info)

        #El if evita que esta parte de código se ejecute si no se logra acceder al canal bienvenida
        if canal_b != None:
            mensaje_b = bienvenida["mensaje"]
            mensaje_b = mensaje_b.replace("{user}", f"{member.mention}")
            mensaje_b = mensaje_b.replace("{server}", f"{member.guild.name}")

            nacionalidad = "Sin nacionalidad"
            if "nacionalidad" in server_conf:
                nacionalidad = server_conf["nacionalidad"]

            file = await imgdni(member.avatar, member.joined_at, member.guild.icon, member.display_name, member.id, nacionalidad)
            try:
                await canal_b.send(mensaje_b, file=file)
            except discord.HTTPException:
                await sleep(3)
                await canal_b.send(mensaje_b, file=file)
            except:
                print("Error no reconocido al intentar enviar el mensaje de bienvenida\nDatos del error:")
                for info in sys.exc_info():
                    print(info)
            file.close()

    if "nuevo_miembro_role" in server_conf:
        role_newmem_id = int(server_conf["nuevo_miembro_role"])

        try:
            role_newmem = discord.utils.get(member.guild.roles, id=role_newmem_id)
            await member.add_roles(role_newmem)
        except discord.NotFound:
            Datos.remove("servers/"+server_id+"/configs/nuevo_miembro_role")

#Esta función se ejecuta si el bot es añadido a un nuevo servidor
@bot.event
async def on_guild_join(guild):
    def_server = Datos.get("servers/def_n_server")
    Datos.update("servers", {str(guild.id): def_server})
    Datos.update("servers list", {str(guild.id): 0})
    print(f"He añadido el servidor: {guild.id} a la lista de servidores.")

#Esta función se ejecuta si el bot es removido de un servidor
@bot.event
async def on_guild_remove(guild):
    Datos.remove("servers/"+str(guild.id))

#Esta función se ejecuta si un miembro sale del servidor
@bot.event
async def on_member_remove(member):
    """"Lo que hace es mandar un mensaje de despedida,
    en dado caso que el server tenga la configuración activada y
    quita los niveles acumulados por habla."""

    server_id = str(member.guild.id)
    server_conf = Datos.get("servers/"+server_id+"/configs")
    miembro_id = str(member.id)

    if "canal_despedida" in server_conf:
        canal_d_id = int(server_conf["canal_despedida"]["canal"])
        mensaje_d = server_conf["canal_despedida"]["mensaje"]
        mensaje_d = mensaje_d.replace("{user}", f"{member.display_name}")

        Datos.remove("servers/"+server_id+"/miembros/"+miembro_id+"/nivel")
        
        try:
            channel = bot.get_channel(canal_d_id)
            despedida = await channel.send(mensaje_d)
            await despedida.add_reaction('👋')
        except:
            pass

#Comando que enseña el dni de un integrante y manda una alerta si el miembro no tiene permiso para usar ese comando
#@bot.slash_command(guilds_id=[730084778061332550])
@bot.command(aliases=['cedula', 'documento', 'cédula'])
async def dni(ctx : Union[commands.Context, discord.ApplicationContext], person : discord.Member = None):
    server_id = str(ctx.guild.id)
    server_conf = Datos.get("servers/"+server_id+"/configs")
    canales_comandos = Datos.get("servers/"+server_id+"/canales_comandos")
    idioma = server_conf["idioma"]

    #Esta parte determina si el usuario puede o no usar este comando en el canal que fue ejecutado
    permisoconcedido = False
    if ctx.author.guild_permissions.administrator:
        permisoconcedido = True
    else:
        if canales_comandos != False:
            canal_id = str(ctx.channel.id)
            if canal_id in canales_comandos:
                permisoconcedido = True
            elif canales_comandos == True:
                permisoconcedido = True

    if permisoconcedido:
        nacionalidad = "Sin nacionalidad"
        if "nacionalidad" in server_conf:
            nacionalidad = server_conf["nacionalidad"]

        if person == None:
            person = ctx.author
        avatar = person.avatar
        fecha_ingreso = person.joined_at
        grupo_logo = ctx.guild.icon
        nombre = person.display_name
        identificador = person.id
        file = await imgdni(avatar, fecha_ingreso, grupo_logo, nombre, identificador, nacionalidad)
        if isinstance(ctx, commands.Context):
            await ctx.reply(file=file)
            file.close()
        else:
            return file
    else:
        aviso = None
        if canales_comandos == False:
            msg = idiomas.cell_value(55, idioma)
            aviso = await ctx.message.reply(f"{msg}")

        else:
            msg = idiomas.cell_value(1, idioma)
            canales = ""

            for canal in canales_comandos:
                canales += f" <#{canal}>"

            msg = msg.replace("{canales}", canales)
            aviso = await ctx.reply(f"{msg}")

        await sleep(5)
        try:
            await aviso.delete()
        except discord.NotFound:
            pass

@bot.slash_command(
    guilds_id=[730084778061332550],
    name=f"{prefijo}dni",
    description="Muestra el dni de una persona."
)
@option(
    "person",
    discord.Member,
    description="La persona a la que le quieres ver el dni, por defecto tú mismo.",
    required=False,
    default=None,
    guild_only=True
)
async def dni1(ctx : discord.ApplicationContext, person):
    respuesta = await ctx.respond("...")
    file = await dni(ctx, person)
    await respuesta.edit_original_message(content=None, file=file)
    file.close()

#Comando para borrar mensajes
@bot.command(aliases=['borrar', 'msgkill', 'delete'])
async def clear(ctx : commands.Context, cant : int = 0):
    server_id = str(ctx.message.guild.id)
    server_conf = Datos.get("servers/"+server_id+"/configs")
    idioma = server_conf["idioma"]

    #Sólo los administradores pueden ejecutar este mensaje
    if ctx.author.guild_permissions.administrator:
        if cant > 0 and cant <= 300:
            borrados = 0
            if not ctx.message.mentions:
                borrados = await ctx.channel.purge(limit=cant)
            else:
                borrados = await ctx.channel.purge(limit=cant, check=ctx.message.mentions[0])

            msg = idiomas.cell_value(3, idioma)
            msg = msg.replace("{cant}", f"{len(borrados)}")
            listo = await ctx.send(msg)
            await sleep(3)
            try:
                await listo.delete()
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

@bot.command()
async def refresh(ctx : commands.Context, cog : str):
    if ctx.author.id == 345737329383571459:
        print(f"Actualizando la extensión {cog}...")
        bot.reload_extension(f"cogs.{cog}")
        print(f"Extensión {cog} actualizada.")

#Mensaje de error
"""@bot.event
async def on_command_error(ctx, error):
    print(error)"""


"""for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        if filename != "FireBaseGestor.py" and filename != "embeds.py":"""
bot.load_extension(f'cogs.moderacion')

#Ejecuta el bot
#bot.run(getenv("DISCORD_SECRET_KEY"))
bot.run(getenv("prueba_bot"))