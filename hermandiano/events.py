from hermandiano import bot, Datos, exl, imgdni
import discord
from random import randint
from threading import Thread
import sys
from asyncio import sleep

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
    def pageweb():
        import hermandiano.WebPage.index
    t = Thread(target=pageweb)
    t.start()
    
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