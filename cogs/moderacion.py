import discord
from discord.ext import commands
from time import sleep as sleep2
from asyncio import sleep, run
from xlrd import open_workbook as open_excel
from cogs.FireBaseGestor import Bot_DB
from datetime import date, timedelta, datetime
import cogs.embeds as embeds
import re
#from threading import Thread as th
from concurrent.futures import ThreadPoolExecutor as hilo

#Variables universales
excel = open_excel("cogs\\idiomas.xlsx")
bot_i = excel.sheet_by_name("bot")
Datos = Bot_DB()
fecha_formato = "%d/%m/%Y %H:%M"

class ModeracionCommands(commands.Cog):
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    def permiso(self, member : discord.Member, server_config):
        """Esta función revisa si el usuario puede usar el comando que trató de ejecutar"""

        permiso = False
        if member.guild_permissions.administrator:
            permiso = True

        elif "role_mod" in server_config:
            if member.get_role(int(server_config["role_mod"])) != None:
                permiso = True

        return permiso
    
    async def revision(self, member : discord.Member, ctx : commands.Context, server_config, idioma):
        """Esta función revisa si el usuario puede usar los comandos de moderación en x persona
        y le avisa en caso de que no"""

        permiso = True
        if member.guild_permissions.administrator:
            permiso = False
            await self.adver_ad(idioma, 41, ctx)

        elif "role_mod" in server_config:
            if member.get_role(server_config["role_mod"]) != None:
                if not ctx.author.guild_permissions.administrator:
                    permiso = False
                    await self.adver_ad(idioma, 42, ctx)

        return permiso

    async def silenciar_tban(self, member : discord.Member, tiempo, sil_tban : bool, role = None):
        """Esta función administra silencios temporales y baneos temporales.
        Se encarga de aplicarlos y de quitarlos"""

        #true silenciar
        #false tban
        if sil_tban:
            if role != None:
                await member.add_roles(role)
                await sleep(tiempo)
                await member.remove_roles(role)

        else:
            await member.ban()
            await sleep(tiempo)
            await member.unban()

    async def error_01(self, ctx : commands.Context, idioma):
        """Este es el mensaje que se le muestra al usuario si
        no tiene permisos para usar un comando"""

        adver = await ctx.reply(f'{bot_i.cell_value(5, idioma)}')
        await sleep(3)

        try:
            await adver.delete()
        except discord.NotFound:
            pass

        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass

    async def adver_ad(self, idioma : int, oracion : int, ctx : commands.Context):
        """Mensaje de advertencia"""

        adver = await ctx.reply(f'{bot_i.cell_value(oracion, idioma)}')
        await sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass

    @commands.command()
    async def tempmute(self, ctx : commands.Context, member : discord.Member = None, tiempo : int = 0, *, razon : str = "Sin especificar"):
        server_id = str(ctx.message.guild.id)
        server_conf = Datos.get("servers/"+server_id+"/configs")
        idioma = server_conf["idioma"]

        if self.permiso(ctx.author, server_conf):
            compro_de_datos = True #True = Todos los datos están bien
            moderador = ctx.author
            member_id = str(member.id)

            if member == None:
                compro_de_datos = False
                await self.adver_ad(idioma, 39, ctx)
            else:
                compro_de_datos = await self.revision(member, ctx, server_conf, idioma)

            if tiempo <= 0 or tiempo > 180:
                compro_de_datos = False
                await self.adver_ad(idioma, 54, ctx)

            if compro_de_datos:
                try:
                    await member.edit(mute=True)
                except discord.errors.HTTPException:
                    pass

                member_data = Datos.get("servers/"+server_id+"/miembros/"+member_id)
                cast_mods = 0
                if member_data != None:
                    if "castigos_mod" in member_data:
                        cast_mods = len(member_data["castigos_mod"])

                fecha = datetime.today().strftime("%d/%m/%Y %H:%M")
                cast_data = {
                    str(cast_mods): {
                        "castigo": 2,
                        "por": str(moderador.id),
                        "razon": razon,
                        "fecha": fecha
                    }
                }

                tiempo = 60 * tiempo
                role_s = None
                if "role_silencio" in server_conf:
                    role_s = ctx.guild.get_role(int(server_conf["role_silencio"]))
                
                parametros = {
                    "member": member,
                    "tiempo": tiempo,
                    "sil_tban": True,
                    "role": role_s
                }
                hilo().submit(self.segundo_hilo, args=[True, self.silenciar_tban, None, parametros])
                #th(self.segundo_hilo, args=[True, self.silenciar_tban, None, parametros]).start()

                if member_data == None:
                    Datos.set_data(f"servers/{server_id}/miembros/{member_id}", {"castigos_mod" : cast_data})
                else:
                    if cast_mods == 0:
                        Datos.set_data(f"servers/{server_id}/miembros/{member_id}/castigos_mod", cast_data)
                    else:
                        Datos.update(f"servers/{server_id}/miembros/{member_id}/castigos_mod", cast_data)

                if "mod_log" in server_conf:
                    mod_embed = embeds.mod_embed(moderador, member, 2, idioma, 46, razon)
                    min_str = 0
                    if tiempo == 1:
                        min_str = f"{tiempo} Minuto"
                    else:
                        min_str = f"{tiempo} Minutos"

                    mod_embed.add_field(
                        name=str(bot_i.cell_value(54, idioma)),
                        value=min_str
                    )
                    canal = ctx.guild.get_channel(server_conf["mod_log"])
                    await canal.send(embed=mod_embed)

        else:
            await self.error_01(ctx, idioma)

    @commands.command(aliases=["aviso"])
    async def warn(self, ctx : commands.Context, member : discord.Member = None, *, razon : str = "Sin especificar"):
        server_id = str(ctx.message.guild.id)
        server_conf = Datos.get("servers/"+server_id+"/configs")
        idioma = server_conf["idioma"]

        if self.permiso(ctx.author, server_conf):
            compro_de_datos = True #True = Todos los datos están bien
            moderador = ctx.author

            if member == None:
                compro_de_datos = False
                await self.adver_ad(idioma, 39, ctx)
            else:
                compro_de_datos = await self.revision(member, ctx, server_conf, idioma)

            if compro_de_datos:
                await self.advertencia()

        else:
            self.error_01(ctx, idioma)

    def warns_tiempo(self, castigo, start):
        tiempo = str(castigo[start+"dias"])
        if castigo[start+"dias"] == 1:
            tiempo = tiempo + " día, "
        else:
            tiempo = tiempo + " días, "
        if castigo[start+"horas"] == 1:
            tiempo = tiempo + str(castigo[start+"horas"]) + " hora, "
        else:
            tiempo = tiempo + str(castigo[start+"horas"]) + " horas, "
        if castigo["en_minutos"] == 1:
            tiempo = tiempo + str(castigo[start+"minutos"]) + " minuto"
        else:
            tiempo = tiempo + str(castigo[start+"minutos"]) + " minutos"
        return tiempo

    #Esta funcion se encarga de enviar cualquier modificación hecha al canal de moderación
    async def canal_moderador(self, server_conf, msg = None, embed = None, file = None):
        if "canal_moderacion" in server_conf:
            canal_moderacion = server_conf["canal_moderacion"]
            try:
                canal = self.bot.get_channel(int(canal_moderacion))
                await canal.send(content=msg, embed=embed, file=file)
            except discord.NotFound:
                pass

    async def accion_i(self, accion : int, canal : discord.TextChannel, mensaje_av : str, mensaje_adv : str = None, msg : discord.Message = None):
        """Esta función se encarga de advertir al usuario y borrar su mensaje
        en caso de que este haya cometido una infracción"""
        
        """
        accion = 1, advertir pero no borrar el mensaje
        accion = 2, borrar el mensaje pero no advertir
        accion = 3, advertir y borrar el mensaje
        En todos los casos se le avisa al usuario que lo que hizo está mal
        """
        if accion == 1:
            aviso = await canal.send(mensaje_av)
            hilo().submit(self.segundo_hilo, args=[True, aviso.delete, 3])
            self.advertencia()

    #Atrapa todos los mensajes enviados
    @commands.Cog.listener()
    async def on_message(self, msg : discord.Message):
        """Esta función detecta todos los mensajes y los analiza,
        siempre y cuando, no sea de un bot."""

        if not msg.author.bot:
            server_id = str(msg.guild.id)
            server_conf = Datos.get(f"servers/{server_id}/configs")
            msj_content = msg.content
            msj_author = msg.author
            msj_channel = msg.channel
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
                avisos = []
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

                if invites_urls:
                    allow_invites = Datos.get(f"servers/{server_id}/allow_invites")
                    if isinstance(allow_invites, list):
                        #Revisa si el mensaje tiene links a otros servers de discord
                        #Si es así, lo penalizará si fue enviado en un canal no permitido
                        if allow_invites["canales"] == 0 or not str(msg.channel.id) in allow_invites["canales"]:
                            avisos.append()

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
                                """apto_sub = False
                                mensaje = bot_i.cell_value(43, idioma).replace("{palabra}", palabra)
                                razon = f"Haber dicho ||{palabra}||\n**Mensaje:**\n{msg.content}"
                                moderador = msg.guild.get_member(736966021528944720) #bot id

                                await self.advertencia()
                                try:
                                    await msg.delete()
                                except discord.NotFound:
                                    pass
                                break"""

                        if len(palabras) != 0:
                            apto_sub = p_prohibidas["level_up"]
                            accion = p_prohibidas["accion"]
                            if accion == 0:
                                pass
                
                        
                """if not allowed_invite:
                    mensaje = "En este canal no está permitido enviar invitaciones a otros servers."
                    razon = "Enviar una invitación a otro server en un canal no permitido."
                    moderador = msg.guild.get_member(736966021528944720) #bot id

                    await self.advertencia()"""

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
                        await self.nivel_social(msg, server_conf["niveles"], str(msg.author.id))
                else:
                    await self.nivel_social(msg, server_conf["niveles"], server_id, str(msg.author.id))
    
    #Esta funcion advierte al usuario so cometió alguna infracción
    #Y la registra para un futuro castigo si el usuario sigue haciendo infracciones
    #También aplica el castigo
    async def advertencia(self, miembro : discord.Member, razon : str, server_id : str, moderador : discord.Member, server_conf, mensaje : str = None):
        member_id = str(miembro.id)
        idioma = server_conf["idioma"]

        hoy = datetime.today()

        #Revisa si el miembro existe en la base de datos y si ya tiene avisos previos
        avisos = Datos.get(f"servers/{server_id}/miembros/{member_id}/avisos")
        avisos_cant = 0
        if avisos != None:
            avisos_cant = len(avisos)
        else:
            avisos = []

        #Nuevo aviso
        aviso = {
            str(avisos_cant):{
                "por": str(moderador.id),
                "razon": razon,
                "fecha": hoy.strftime(fecha_formato)
            }
        }

        Datos.update(f"servers/{server_id}/miembros/{member_id}/avisos",  aviso)
        mod_embed = embeds.mod_embed(moderador, miembro.mention, 1, idioma, 45, razon)
        await self.canal_moderador(server_conf, embed=mod_embed)

        avisos.append(aviso[str(avisos_cant)])
        
        #En caso de que se hayan configurados los castigos
        castigos = Datos.get(f"servers/{server_id}/castigos")
        if castigos != None:
            castigos_aplicar = []
            cant_avisos = len(avisos)-1
            castigos_aplicados = Datos.get(f"servers/{server_id}/miembros/{member_id}/castigos aplicados")
            for c in castigos:
                castigo = castigos[c]
                """Los castigos son activados según 3 factores: La cantidad de avisos hechos,
                hace cuanto fue advertido al miembro y si ese castigo ya ha sido aplicado en
                un cierto periodo de tiempo."""

                if castigos["cant_warns"] <= cant_avisos:
                    seguir = True
                    #Revisa si el miembro tiene suficientes advertencias
                    if castigos_aplicados != None:
                        if c in castigos_aplicados:
                            ult_apl_cast = datetime.strptime(castigos_aplicados[c], fecha_formato)
                            #Revisa si al usuario ya se le ha aplicado el castigo en el tiempo del cooldown
                            if (hoy - ult_apl_cast).days < castigo["cooldown"]:
                                seguir = False

                    #Revisa si la cantidad de advertencias se hicieron en el periodo de aplicación del castigo
                    if seguir:
                        aviso_ver = avisos[cant_avisos-castigo["cant_warns"]]
                        aviso_fecha = datetime.strptime(aviso_ver["fecha"], "%d/%m/%Y %H:%M")
                        tiempo_ad = castigo["tiempo_ad"]["dias"]*24*60*60
                        tiempo_ad += castigo["tiempo_ad"]["horas"]*60*60
                        fecha_ver = hoy - timedelta(seconds=tiempo_ad)
                        if fecha_ver >= aviso_fecha:
                            seguir = True
                    
                    if seguir:
                        role = None
                        if "role_silencio" in server_conf:
                            try:
                                role = self.bot.get_guild(int(server_id)).get_role(int(server_conf["role_silencio"]))
                            except discord.NotFound:
                                pass
                        tiempo = castigo["dura"]["dias"]*24*60*60
                        tiempo += castigo["dura"]["horas"]*60*60
                        tiempo += castigo["dura"]["minutos"]*60
                        parametros = {
                            "member": miembro,
                            "tiempo": tiempo,
                            "role": role
                        }

                        informacion = f"El miembro {miembro.mention} fue "
                        accion = None
                        if castigo["castigo"] == 2:
                            informacion += "silenciado por "
                            parametros["sil_tban"] = True
                        elif castigo["castigo"] == 3:
                            informacion += "baneado por "
                            parametros["sil_tban"] = False
                        elif castigo["castigo"] == 4:
                            informacion += "expulsado por "
                            accion = miembro.kick
                        elif castigo["castigo"] == 5:
                            informacion += "baneado permantentemente "
                            accion = miembro.ban
                        
                        if castigo["castigo"] < 4:
                            informacion += castigo["dura"]["dias"]+" día(s) "
                            informacion += castigo["dura"]["horas"]+" horas y "
                            informacion += castigo["dura"]["minutos"]+" minútos "
                            
                        informacion += "por acumular "+castigo["cant_warns"]+" advertencias en menos de "
                        informacion += castigo["tiempo_ad"]["dias"]+" día(s) y "
                        informacion += castigo["tiempo_ad"]["horas"]+" horas"

                        if castigo["castigo"] < 4:
                            hilo().submit(self.segundo_hilo, args=[True, self.silenciar_tban, None, parametros])
                        else:
                            await accion(reason=informacion)
                        
                        Datos.update(f"servers/{server_id}/members/{member_id}/castigos aplicados", {c:hoy.strftime(fecha_formato)})
                        member_castigos = Datos.get(f"servers/{server_id}/members/{member_id}/castigos")
                        Datos.update(f"servers/{server_id}/members/{member_id}/castigos", {
                            str(len(member_castigos)):{
                                "id": c,
                                "fecha": hoy.strftime(fecha_formato),
                                "informacion": informacion
                            }
                        })
                        mod_embed = embeds.mod_embed(moderador, miembro.mention, castigo["castigo"], idioma, 46, informacion)
                        await self.canal_moderador(server_conf, embed=mod_embed)

    async def nivel_social(self, msg : discord.Message, xp_up, server_id, member_id):
        roles_nivel = Datos.get(f"servers/{server_id}/roles_nivel")
        if roles_nivel != None and isinstance(roles_nivel, list):
            r = {}
            i = 0
            for role in roles_nivel:
                if role != None:
                    r[str(i)] = role
                i += 1
            roles_nivel = r

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
                    await msg.channel.send(mensaje)

                if roles_nivel != None:
                    if str(data_nivel["nivel"]) in roles_nivel:
                        try:
                            role = msg.guild.get_role(int(roles_nivel[str(data_nivel["nivel"])]))
                            await msg.author.add_roles(role)
                        except discord.NotFound:
                            pass
            else:
                data_nivel["xp"] += xp_up
    
    def segundo_hilo(self, is_async : bool, funcion, tiempo : float = None, parametros : dict = None):
        """Esta función se usa para que otras funciones se ejecuten en segundo plano"""

        async def do_something_sc(funcion2, tiempo = None, parametros = None):
            if tiempo != None:
                await sleep(tiempo)

            if parametros == None:
                await funcion2()
            else:
                await funcion2(**parametros)

        if is_async:
            run(do_something_sc(funcion, tiempo, parametros))
        else:
            if tiempo != None:
                sleep2(tiempo)

            if parametros == None:
                funcion()
            else:
                funcion(**parametros)

def setup(bot):
    bot.add_cog(ModeracionCommands(bot))