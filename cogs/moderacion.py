import discord
from discord.ext import commands
from asyncio import sleep, get_event_loop
from xlrd import open_workbook as open_excel
import cogs.FireBaseGestor as Datos
from datetime import date, timedelta, datetime
import cogs.embeds as embeds
import re

excel = open_excel("cogs\\idiomas.xlsx")
bot_i = excel.sheet_by_name("bot")

class ModeracionCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    def permiso(self, member, server_conf):
        """Esta función revisa si el usuario puede usar los comandos de moderación
        y le avisa en caso de que no"""

        permiso = False
        if member.guild_permissions.administrator:
            permiso = True
        else:
            if "roles_moderador" in server_conf:
                for role in member.roles:
                    if str(role.id) in server_conf:
                        permiso = True
                        break
        return permiso
    
    async def revision(self, member : discord.Member, moderador : discord.Member, server_config, idioma, canal):
        """Esta función revisa si el usuario puede usar los comandos de moderación en x persona
        y le avisa en caso de que no"""

        permiso = True
        if member.guild_permissions.administrator:
            permiso = False
            await self.adver_ad(idioma, 41, canal, moderador.mention)
        
        if "roles_moderador" in server_config and permiso:
            for role in member.roles:
                if str(role.id) in server_config["roles_moderador"]:
                    if not moderador.guild_permissions.administrator:
                        permiso = False
                        await self.adver_ad(idioma, 42, canal, moderador.mention)
                    break
        return permiso

    async def silenciar_tban(self, member, tiempo, sil_tban, role = None):
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

    async def error_01(self, mensaje, canal, miembro, idioma):
        """Este es el mensaje que se le muestra al usuario si
        no tiene permisos para usar un comando"""

        try:
            await mensaje.delete()
        except discord.NotFound:
            pass
        adver = await canal.send(f'{miembro.mention} {bot_i.cell_value(5, idioma)}')
        await sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass

    async def adver_ad(self, idioma : int, oracion : int, canal, mencionar):
        """Mensaje de advertencia"""

        adver = await canal.send(f'{mencionar} {bot_i.cell_value(oracion, idioma)}')
        await sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass

    @commands.command()
    async def tempmute(self, ctx : commands.Context, member : discord.Member = None, tiempo : int = 0, *, razon : str = None):
        server_id = str(ctx.message.guild.id)
        server_conf = Datos.getdata("servers/"+server_id+"/configs")
        idioma = server_conf["idioma"]

        if self.permiso(ctx.author, server_conf):
            compro_de_datos = True #True = Todos los datos están bien
            moderador = ctx.author
            member_id = str(member.id)

            if razon == None:
                razon = "Sin especificar"

            if member == None:
                compro_de_datos = False
                await self.adver_ad(idioma, 39, ctx.channel, ctx.author.mention)
            else:
                compro_de_datos = await self.revision(member, moderador, server_conf, idioma, ctx.channel)

            if tiempo <= 0 or tiempo > 180:
                compro_de_datos = False
                await self.adver_ad(idioma, 54, ctx.channel, ctx.author.mention)

            if compro_de_datos:
                try:
                    await member.edit(mute=True)
                except discord.errors.HTTPException:
                    pass

                member_data = Datos.getdata("servers/"+server_id+"/miembros/"+member_id)
                cast_mods = 0
                if member_data != None:
                    if "castigos_mod" in member_data:
                        cast_mods = len(member_data["castigos_mod"])

                cast_data = {
                    str(cast_mods): {
                        "castigo": 2,
                        "por": str(moderador.id),
                        "razon": razon
                    }
                }

                if member_data == None:
                    Datos.update_adddata("servers/"+server_id+"/miembros", {member_id: {"castigos_mod" : cast_data}})
                else:
                    if cast_mods == 0:
                        Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id, {"castigos_mod":cast_data})
                    else:
                        Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/castigos_mod", cast_data)

                mod_embed = embeds.mod_embed(moderador, member, 2, idioma, 46, razon)

                min_str = None
                if tiempo == 1:
                    min_str = f"{tiempo} Minuto"
                else:
                    min_str = f"{tiempo} Minutos"

                mod_embed.add_field(
                    name=str(bot_i.cell_value(54, idioma)),
                    value=min_str
                )
                await self.canal_moderador(server_conf, embed=mod_embed)

                tiempo = 60 * tiempo
                role_s = None
                if "role_silencio" in server_conf:
                    role_s = discord.utils.get(ctx.guild.roles, id=int(server_conf["role_silencio"]))

                await self.silenciar_tban(member, tiempo, True, role_s)

        else:
            await self.error_01(ctx, idioma)

    @commands.command(aliases=["aviso"])
    async def warn(self, ctx : commands.Context, member : discord.Member = None, *, razon : str = None):
        server_id = str(ctx.message.guild.id)
        server_conf = Datos.getdata("servers/"+server_id+"/configs")
        idioma = server_conf["idioma"]

        if self.permiso(ctx.author, server_conf):
            compro_de_datos = True #True = Todos los datos están bien
            moderador = ctx.author
            member_id = str(member.id)

            if razon == None:
                razon = "Sin especificar"

            if member == None:
                compro_de_datos = False
                await self.adver_ad(idioma, 39, ctx.channel, ctx.author.mention)
            else:
                compro_de_datos = await self.revision(member, moderador, server_conf, idioma, ctx.channel)

            if compro_de_datos:
                await self.advertencia(
                    ctx.channel,
                    member,
                    razon,
                    server_id,
                    moderador,
                    idioma,
                    server_conf
                )

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

    async def canal_moderador(self, server_conf, msg = None, embed = None, file = None):
        if "canal_moderacion" in server_conf:
            canal_moderacion = server_conf["canal_moderacion"]
            try:
                canal = self.bot.get_channel(int(canal_moderacion))
                await canal.send(content=msg, embed=embed, file=file)
            except discord.NotFound:
                pass

    async def notificacion_castigo(self, castigo, idioma, moderador, miembro, server_conf, castigo_nivel):
        razon = ""
        if castigo["cant_warns"] == 1:
            razon = str(bot_i.cell_value(51, idioma))
        else:
            razon = str(bot_i.cell_value(50, idioma))
            razon = razon.replace("{cant}", str(castigo["cant_warns"]))
            
        tiempo = self.warns_tiempo(castigo, "en_")
        razon = razon.replace("{tiempo}",tiempo)

        notificacion = embeds.mod_embed(moderador, miembro, castigo_nivel, idioma, 46, razon)
        if castigo_nivel < 4:
            tiempo = self.warns_tiempo(castigo, "dura_")
            notificacion.add_field(
                name=str(bot_i.cell_value(54, idioma)),
                value=tiempo,
                inline=False
            )
        await self.canal_moderador(server_conf, embed=notificacion)

    #Atrapa todos los mensajes enviados
    @commands.Cog.listener()
    async def on_message(self, msg : discord.Message):
        if not msg.author.bot:
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
            if "palabras_prohibidas" in server_conf: #and not msg.author.guild_permissions.administrator:
                async def palabra_prohibida():
                    msj = msg.content.lower().lower().split(" ")
                    for palabra in server_conf["palabras_prohibidas"]:
                        if palabra in msj:
                            apto_sub = False
                            mensaje = bot_i.cell_value(43, idioma).replace("{palabra}", palabra)
                            razon = f"Haber dicho ||{palabra}||\n**Mensaje:**\n{msg.content}"
                            moderador = msg.guild.get_member(736966021528944720) #bot id

                            await self.advertencia(
                                msg.channel,
                                msg.author,
                                razon,
                                server_id,
                                moderador,
                                idioma,
                                server_conf,
                                mensaje
                            )
                            try:
                                await msg.delete()
                            except discord.NotFound:
                                pass
                            break
                if "canal_pp_aceptadas" in server_conf:
                    if not str(msg.channel.id) in server_conf:
                        await palabra_prohibida()
                else:
                    await palabra_prohibida()
            
            if server_conf["no_discordinvite_links"]:
                if not server_conf["discordivite_links_allow"] == str(msg.channel.id):
                    patron = r".*(https:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.[A-Za-z]+"
                    if re.match(patron, msg.content):
                        if "canales_intive_p" in server_conf:
                            if not str(msg.channel.id) in server_conf["canales_intive_p"]:
                                apto_sub = False
                                mensaje = "En este canal no está permitido enviar invitaciones a otros servers."
                                razon = "Enviar una invitación a otro server en un canal no permitido."
                                moderador = msg.guild.get_member(736966021528944720) #bot id

                                await self.advertencia(
                                    msg.channel,
                                    msg.author,
                                    razon,
                                    server_id,
                                    moderador,
                                    idioma,
                                    server_conf,
                                    mensaje
                                )

            if server_conf["niveles_habla"] and apto_sub:
                if "no_xp_channels" in server_conf:
                    if not str(msg.channel.id) in server_conf["no_xp_channels"]:
                        await self.nivel_social(miembro, database, server, msg.guild, msg.author)
                else:
                    await self.nivel_social(miembro, database, server, msg.guild, msg.author)
    
    async def advertencia(self, canal, miembro : discord.Message, razon, server_id, moderador, idioma, server_conf, mensaje = None):
        member_id = str(miembro.id)

        if mensaje != None:
            adver = await canal.send(f"{miembro.mention} {mensaje}")
            get_event_loop().create_task(self.do_something_sc(adver.delete, 5))

        fecha = datetime.today()

        member_data = Datos.getdata("servers/"+server_id+"/miembros/"+member_id)
        avisos_cant = 0
        if member_data != None:
            if "avisos" in member_data:
                avisos_cant = len(member_data["avisos"])-1

        aviso = {
            str(avisos_cant):{
                "por": str(moderador.id),
                "razon": razon,
                "fecha": fecha.strftime("%d/%m/%Y %H:%M"),
                "cast_apl": {
                    "ddd": True
                }
            }
        }

        if member_data == None:
            Datos.update_adddata("servers/"+server_id+"/miembros", {member_id: {"avisos" : {"cast_apl": {"ddd":True}}}})
            Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/avisos", aviso)
        else:
            if avisos_cant == 0:
                Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id, {"avisos" : {"cast_apl": {"ddd":True}}})
                Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/avisos", aviso)
            else:
                Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/avisos", aviso)

        mod_embed = embeds.mod_embed(moderador, miembro, 1, idioma, 45, razon)
        await self.canal_moderador(server_conf, embed=mod_embed)

        avisos = Datos.getdata("servers/"+server_id+"/miembros/"+member_id+"/avisos")
        await self.cast_apl(server_conf, avisos, fecha, server_id, member_id, idioma, moderador, miembro, miembro.guild.roles)

    async def nivel_social(self, miembro : discord.Member, member_data, server_conf, canal):
        data_nivel = {}
        xp_up = server_conf["xp_x_msg"]
        if member_data == None:
            data_nivel["nivel"] = 1
            data_nivel["xp"] = xp_up
            data_nivel["nxtniv"] = 100

        elif not "nivel" in member_data:
            data_nivel["nivel"] = 1
            data_nivel["xp"] = xp_up
            data_nivel["nxtniv"] = 100

        else:
            member_level = member_data["nivel"]
            xp = member_level["xp"]
            nxtniv = member_level["nxtniv"]
            if (xp+xp_up) >= nxtniv:
                data_nivel["xp"] = 0
                data_nivel["nxtniv"] = int(nxtniv + (nxtniv * 0.5))
                data_nivel["nivel"] = member_level["nivel"] + 1

                if canal != None:
                    mensaje = server_conf["canal_level_up"]["mensaje"]
                    mensaje = mensaje.replace("{user}", f"{miembro.mention}")
                    mensaje = mensaje.replace("{nivel}", f"{data_nivel['nivel']}")
                    await canal.send(mensaje)

                if "niv_roles" in server_conf:
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

    async def cast_apl(self, server_conf, avisos, fecha, server_id, member_id, idioma, moderador, member, g_roles):
        if "castigos" in server_conf:
            castigos_aplicar = []
            for castigo in server_conf["castigos"]:
                cant_avisos = len(avisos)-1
                if castigo["cant_warns"] <= cant_avisos:
                    apl_castigo = True
                    aviso_ver = avisos[str(cant_avisos-castigo["cant_warns"])]
                    seguir = False
                    if str(castigo["id"]) in avisos["cast_apl"]:
                        ult_cast_apl = datetime.strptime(avisos["cast_apl"][str(castigo["id"])], "%d/%m/%Y %H:%M")
                        fecha_ver = fecha - timedelta(server_conf["castigos_cooldown"])

                        if (fecha_ver - ult_cast_apl).days >= 0:
                            seguir = True
                    else:
                        seguir = True

                    if not str(castigo["id"]) in aviso_ver["cast_apl"] and seguir:
                        fecha_ver = fecha - timedelta(castigo["en_dias"], (castigo["en_horas"]*60*60)+(castigo["en_minutos"]*60))
                        fecha_ver2 = fecha_ver2 = datetime.strptime(aviso_ver["fecha"], "%d/%m/%Y %H:%M")
                        tiempo = ((fecha_ver - fecha_ver2).days*24*60*60) + (fecha_ver - fecha_ver2).seconds

                        if tiempo < 60:
                            castigos_aplicar.append(castigo)

                            Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/avisos/cast_apl", {str(castigo["id"]): fecha.strftime("%d/%m/%Y %H:%M")})
                            for aviso_num in range(cant_avisos-castigo["cant_warns"], cant_avisos):
                                Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/avisos/"+str(aviso_num)+"/cast_apl", {str(castigo["id"]): True})

            if len(castigos_aplicar) > 0:
                castigos_aplicar = sorted(castigos_aplicar, key = lambda i:(i["castigo"]), reverse=True)

                if castigos_aplicar[0]["castigo"] > 3:
                    if castigos_aplicar[0]["castigo"] == 4:
                        await self.notificacion_castigo(castigos_aplicar[0], idioma, moderador, member, server_conf, 4)
                        await member.kick()

                    else:
                        await self.notificacion_castigo(castigos_aplicar[0], idioma, moderador, member, server_conf, 5)
                        await member.ban()

                else:
                    role = None
                    if "role_silencio" in server_conf:
                        try:
                            role = discord.utils.get(g_roles, id=int(server_conf["role_silencio"]))
                        except discord.NotFound:
                            pass
                    for castigo in castigos_aplicar:
                        tiempo = (castigo["dura_dias"]*24*60*60) + (castigo["dura_horas"]*60*60) + (castigo["dura_minutos"]*60)
                        await self.notificacion_castigo(castigo, idioma, moderador, member, server_conf, castigo["castigo"])

                        if castigo["castigo"] == 2:
                            get_event_loop().create_task(self.silenciar_tban(member, tiempo, True, role))
                        else:
                            get_event_loop().create_task(self.silenciar_tban(member, tiempo, False))
    
    async def do_something_sc(self, function, tiempo, parametros = None):
        await sleep(tiempo)
        if parametros == None:
            await function()
        else:
            await function(*parametros)

def setup(bot):
    bot.add_cog(ModeracionCommands(bot))
