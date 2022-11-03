from . import bot, Datos
import discord
import re
from moderacion import segundo_hilo
from concurrent.futures import ThreadPoolExecutor as hilo
from moderacion.warn import warn
from discord.ext import commands

@bot.event
async def on_message( msg : discord.Message):
    """Esta función detecta todos los mensajes y los analiza,
    siempre y cuando, no sea de un bot."""

    if not msg.author.bot:
        server_id = str(msg.guild.id)
        server_conf = Datos.get(f"servers/{server_id}/configs")
        msj_content = msg.content
        msj_author = msg.author
        msj_channel = msg.channel
        msj_destroyed = False
        moderador = msg.guild.get_member(736966021528944720) #bot id
        idioma = server_conf["idioma"]

        if "canal_de_memes" in server_conf:
            #Si el servidor tiene un canal, revisará si el mensaje fue enviado en dicho canal
            #Y si el mensaje tiene algún archivo añadirá las reacciones de pulgar arriba y abajo
            if server_conf["canal_de_memes"] == str(msg.channel.id):
                if msg.attachments:
                    await msg.add_reaction('👍')
                    await msg.add_reaction('👎')

        apto_sub = True

        if not msg.author.guild_permissions.administrator:
            #Esta parte detecta si hay un link en el mensaje
            url_detector = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            urls = []
            for url in re.findall(url_detector, msj_content):
                url_u_inicio = re.search(url[0], msj_content).start()
                url_u_final = re.search(url[0], msj_content).end()
                urls.append([url_u_inicio, url_u_final, url[0]])
            
            invites_detector = r".*(https:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.[A-Za-z]+"
            invites_urls = False
            plain_urls = False
            if len(urls) != 0:
                for url in urls:
                    deteccion = re.match(invites_detector, url[2])
                    if deteccion != None:
                        invites_urls = True
                    else:
                        plain_urls = True

            allows = [
                [
                    invites_urls,
                    "allow_invites",
                    f"{msj_author.mention} En este canal no está permitido enviar invitaciones de otros servidores.",
                    "Enviar una invitación en un canal no permitido."
                ],
                [
                    plain_urls,
                    "allow url",
                    f"{msj_author.mention} En este canal no está permitido enviar links.",
                    "Enviar un link en un canal no permitido."
                ]
            ]

            info_db = Datos.get(f"servers/{server_id}/{allow[1]}")
            for allow in allows:
                if allow[0]:
                    if isinstance(info_db, list):
                        #Revisa si el mensaje tiene links a otros servers de discord
                        #Si es así, lo penalizará si fue enviado en un canal no permitido
                        if info_db["canales"] == 0 or not str(msg.channel.id) in info_db["canales"]:
                            aviso = allow[2]
                            advertencia = allow[3]
                            apto_sub = info_db["level_up"]
                            if info_db["accion"] > 1:
                                msj_destroyed = True
                            await accion_i(
                                info_db["accion"],
                                msj_channel,
                                aviso,
                                msj_author,
                                advertencia,
                                msg
                            )

            p_prohibidas = Datos.get(f"servers/{server_id}/palabras prohibidas")
            if p_prohibidas != None: #and not msg.author.guild_permissions.administrator:
                #Revisa si el mensaje contiene alguna palabra prohibida en el servidor
                #Advierte y borra el mensaje, siempre y cuando esté configurado
                if not str(msj_channel.id) in p_prohibidas["canales"]:
                    msj = msj_content.lower().split(" ")
                    palabras = []
                    for palabra in p_prohibidas["palabras"]:
                        if palabra in msj:
                            palabras.append(palabra)

                    if len(palabras) != 0:
                        aviso = f"{msj_author.mention} No puedes utilizar las palabras:\n"
                        for palabra in palabras:
                            aviso += f"||{palabra}||\n"

                        aviso += "En este canal."
                        advertencia = "Usar palabras prohibidas en un canal prohibido."
                        apto_sub = p_prohibidas["level_up"]
                        if info_db["accion"] > 1:
                            msj_destroyed = True
                        await accion_i(
                            info_db["accion"],
                            msj_channel,
                            aviso,
                            msj_author,
                            advertencia,
                            msg
                        )

        no_xp_roles = Datos.get(f"servidores/{server_id}/no_xp_roles")
        if no_xp_roles != None:
            for role in no_xp_roles:
                if msg.author.get_role(role) != None:
                    apto_sub = False
                    break

        if server_conf["niveles"] and apto_sub:
            #Si el tiene los niveles de habla configurados y el mensaje no rompe
            #ninguna regla, este será recompensado con xp
            no_xp = Datos.get(f"servers/{server_id}/no_xp_channels")
            if no_xp != None:
                if not str(msg.channel.id) in no_xp:
                    await nivel_social(msg, server_conf["niveles"], str(msg.author.id))
            else:
                await nivel_social(msg, server_conf["niveles"], server_id, str(msg.author.id))

async def nivel_social(msg : discord.Message, xp_up, server_id, member_id):
    data_nivel = {}
    member = Datos.get(f"servers/{server_id}/miembros/{member_id}")
    mem_lv = None
    if member != None:
        if "nivel" in member:
            mem_lv = member["nivel"]

    if mem_lv == None:
        data_nivel["nivel"] = 1
        data_nivel["xp"] = xp_up
        data_nivel["nxtniv"] = 100

    else:
        data_nivel["xp"] = mem_lv["nivel"]
        data_nivel["nxtniv"] = mem_lv["xp"]
        data_nivel["nivel"] = mem_lv["nxtniv"]
        
    if (data_nivel["xp"]+xp_up) >= data_nivel["nxtniv"]:
        data_nivel["xp"] = data_nivel["xp"] + xp_up - data_nivel["nxtniv"]
        data_nivel["nxtniv"] = int(data_nivel["nxtniv"] + (data_nivel["nxtniv"] * 0.5))
        data_nivel["nivel"] += 1

        mensaje = Datos.get("servers/"+server_id+"/configs/lvl_up_msg")
        if mensaje != None:
            mensaje = mensaje.replace("{user}", f"{msg.author.mention}")
            mensaje = mensaje.replace("{nivel}", f"{data_nivel['nivel']}")
            try:
                await msg.channel.send(mensaje)
            except discord.NotFound:
                pass
            except discord.HTTPException:
                pass
        
        roles_nivel = Datos.get(f"servers/{server_id}/roles_nivel")
        if roles_nivel != None and isinstance(roles_nivel, list):
            r = {}
            i = 0
            for role in roles_nivel:
                if role != None:
                    r[str(i)] = role
                i += 1
            roles_nivel = r

        if roles_nivel != None:
            if str(data_nivel["nivel"]) in roles_nivel:
                try:
                    role = msg.guild.get_role(int(roles_nivel[str(data_nivel["nivel"])]))
                    await msg.author.add_roles(role)
                except discord.NotFound:
                    pass
    else:
        data_nivel["xp"] += xp_up

async def accion_i(
        accion : int,
        canal : discord.TextChannel,
        mensaje_av : str,
        member : discord.Member,
        mensaje_adv: str = None, 
        msg : discord.Message = None
    ):
    """Esta función se encarga de advertir al usuario y borrar su mensaje
    en caso de que este haya cometido una infracción"""
    
    """
    accion = 1, advertir pero no borrar el mensaje
    accion = 2, borrar el mensaje pero no advertir
    accion = 3, advertir y borrar el mensaje
    En todos los casos se le avisa al usuario que lo que hizo está mal
    """
    aviso = await canal.send(mensaje_av)
    hilo().submit(segundo_hilo, args=[True, aviso.delete, 3])

    if accion == 1:
        await warn(ctx=commands.Context(message=msg, bot=bot), member=member, razon=mensaje_adv) #(member, mensaje_adv, server_id, moderador, server_config)

    elif accion == 2:
        await msg.delete()

    elif accion == 3:
        await msg.delete()
        await warn(ctx=commands.Context(message=msg, bot=bot), member=member, razon=mensaje_adv)