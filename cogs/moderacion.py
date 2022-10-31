import discord
from discord.ext import commands
from asyncio import sleep, get_event_loop
from xlrd import open_workbook as open_excel
import cogs.FireBaseGestor as Datos
from datetime import date, timedelta, datetime
import cogs.embeds as embeds

excel = open_excel("cogs\\idiomas.xlsx")
bot_i = excel.sheet_by_name("bot")

class ModeracionCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    def permiso(self, ctx, database, server):
        """Esta función revisa si el usuario puede usar los comandos de moderación
        y le avisa en caso de que no"""

        if ctx.author.guild_permissions.administrator:
            permiso = True
        else:
            if "roles_moderadores" in database["servers"][server]["configs"]:
                for role in ctx.author.roles:
                    if str(role.id) in database["servers"][server]["configs"]["roles_moderadores"]:
                        permiso = True
                        break
        return permiso
    
    async def revision(self, person : discord.Member, ctx, server, database, idioma):
        """Esta función revisa si el usuario puede usar los comandos de moderación en x persona
        y le avisa en caso de que no"""

        compro_de_datos = True
        if person.guild_permissions.administrator:
            compro_de_datos = False
            await self.adver_ad(idioma, 41, ctx, ctx.author.mention)
        
        if "roles_moderadores" in database["servers"][server]["configs"] and compro_de_datos:
            for role in person.roles:
                if str(role.id) in database["servers"][server]["configs"]["roles_moderadores"]:
                    if not ctx.author.guild_permissions.administrator:
                        compro_de_datos = False
                        await self.adver_ad(idioma, 42, ctx, ctx.author.mention)
                    break
        return compro_de_datos

    async def silenciar_tban(self, member, tiempo, sil_tban, role = None):
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

    async def error_01(self, ctx, idioma):
        """Este es el mensaje que se le muestra al usuario si
        no tiene permisos para usar el comando"""

        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass
        adver = await ctx.send(f'{ctx.author.mention} {bot_i.cell_value(5, idioma)}')
        await sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass

    async def adver_ad(self, idioma : int, oracion : int, canal, mencionar):
        adver = await canal.send(f'{mencionar} {bot_i.cell_value(oracion, idioma)}')
        await sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass

    @commands.command()
    async def tempmute(self, ctx, person : discord.Member = None, tiempo = None, *, razon : str = None):
        database = Datos.alldata()
        server = str(ctx.message.guild.id)
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permiso(ctx, database, server):
            compro_de_datos = True #True = Todos los datos están bien

            if razon == None:
                razon = "Sin especificar"

            if person == None:
                compro_de_datos = False
                await self.adver_ad(idioma, 39, ctx, ctx.author.mention)
            else:
                compro_de_datos = await self.revision(person, ctx, server, database, idioma)

            if compro_de_datos:
                try:
                    tiempo = int(tiempo)
                    if tiempo <= 0 or tiempo > 180:
                        compro_de_datos = False
                except:
                    compro_de_datos = False
                    await self.adver_ad(idioma, 54, ctx, ctx.author.mention)

            if compro_de_datos:
                try:
                    await person.edit(mute=True)
                except discord.errors.HTTPException:
                    pass
                if not str(person.id) in database["servers"][server]["miembros"]:
                    database["servers"][server]["miembros"][str(person.id)] = {}

                memberdata = database["servers"][server]["miembros"][str(person.id)]
                if "silenciado" in memberdata:
                    memberdata["silenciado"].append({"por": str(ctx.author.id), "razon": razon})
                else:
                    memberdata["silenciado"] = [{"por": str(ctx.author.id), "razon": razon}]

                Datos.miembro(server, str(person.id), memberdata)

                if "canal_moderacion" in database["servers"][server]["configs"]:
                    seguir = True
                    try:
                        canal = self.bot.get_channel(int(database["servers"][server]["configs"]["canal_moderacion"]))
                        mod_embed = embeds.embed_moderador(ctx.author.mention, person, razon, server, 45, idioma)
                        await canal.send(embed=mod_embed)
                    except discord.NotFound:
                        Datos.delconfig(server, "canal_moderacion")

                tiempo = 60 * tiempo
                silencio = None
                if "role_silencio" in database["servers"][server]["configs"]:
                    try:
                        silencio = discord.utils.get(person.guild.roles, id=int(database["servers"][server]["configs"]["role_silencio"]))
                    except discord.NotFound:
                        Datos.delconfig(server, "role_silencio")

                await quitarsilencio(person, silencio, tiempo)

        else:
            await self.error_01(ctx, idioma)

    @commands.command(aliases=["aviso"])
    async def warn(self, ctx, person : discord.Member = None, *, razon : str = None):
        database = Datos.alldata()
        server = str(ctx.message.guild.id)
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permiso(ctx, database, server):

            if razon == None:
                razon = "Sin especificar"

            if person != None:
                if await self.revision(person, ctx, server, database, idioma):
                    canal = None
                    if "canal_moderacion" in database["servers"][server]["configs"]:
                        try:
                            canal = self.bot.get_channel(int(database["servers"][server]["configs"]["canal_moderacion"]))
                            mod_embed = embeds.embed_moderador(ctx.author.mention, person, razon, server, 47, idioma)
                            await canal.send(embed=mod_embed)
                        except discord.NotFound:
                            Datos.delconfig(server, "canal_moderacion")

                    if not str(person.id) in database["servers"][server]["miembros"]:
                        database["servers"][server]["miembros"][str(person.id)] = {}

                    memberdata = database["servers"][server]["miembros"][str(person.id)]

                    fecha = date.today()
                    if "avisado" in memberdata:
                        memberdata["avisado"].append({"por": str(ctx.author.id), "razon": razon, "fecha": fecha.strftime("%d/%m/%Y")})
                    else:
                        memberdata["avisado"] = [{"por": str(ctx.author.id), "razon": razon, "fecha": fecha.strftime("%d/%m/%Y")}]
                    Datos.miembro(server, str(person.id), memberdata)

                    if "castigos" in database["servers"][server]["configs"]:
                        await cast_apl(server, person, fecha, idioma)

            else:
                await self.adver_ad(idioma, 39, ctx, ctx.author.mention)
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
                canal = bot.get_channel(int(canal_moderacion))
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
                name=f"{bot_i.cell_value(54, idioma)}",
                value=tiempo,
                inline=False
            )
        await self.canal_moderador(server_conf, embed=notificacion)

    #Atrapa todos los mensajes enviados
    @commands.Cog.listener()
    async def on_message(self, msg : discord.Message):
        if not msg.author.bot:
            if msg.content.startswith("p!"):
                await self.bot.process_commands(msg)
        else:
            server_id = str(msg.guild.id)
            member_id = str(msg.author.id)
            server_conf = Datos.getdata("servers/"+server_id+"/configs")
            idioma = server_conf["idioma"]+1

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
                msj = msg.content.lower().split(" ")
                for palabra in server_conf["palabras_prohibidas"]:
                    try:
                        msj.index(palabra)

                        apto_sub = False
                        mensaje = bot_i.cell_value(43, idioma).replace("{palabra}", palabra)

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
                            aviso_numero = len(avisos) -1
                        else:
                            Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/avisos", {"cast_apl": {"ddd":True}})

                        Datos.update_adddata("servers/"+server_id+"/miembros/"+member_id+"/avisos", {str(aviso_numero):aviso})

                        moderador = msg.guild.get_member(736966021528944720) #bot id
                        mod_embed = embeds.mod_embed(moderador, msg.author, 1, idioma, 45, razon)
                        await self.canal_moderador(server_conf, embed=mod_embed)

                        avisos = Datos.getdata("servers/"+server_id+"/miembros/"+member_id+"/avisos")
                        await self.cast_apl(server_conf, avisos, fecha, server_id, member_id, idioma, moderador, msg.author, msg.guild.roles)
                        try:
                            await msg.delete()
                        except discord.NotFound:
                            pass
                        break
                    except:
                        pass

            """if database["servers"][server]["configs"]["niveles_de_habla"] and apto_sub:
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
                    await nivel_social(miembro, database, server, msg.guild, msg.author)"""
    
    async def nivel_social(self, miembro, database, server, guild, author):
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
                            get_event_loop().create_task(silenciar_tban(member, tiempo, True, role))
                        else:
                            get_event_loop().create_task(silenciar_tban(member, tiempo, False))

def setup(bot):
    bot.add_cog(ModeracionCommands(bot))
