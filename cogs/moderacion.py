import discord
from discord.ext import commands
from asyncio import sleep
from xlrd import open_workbook as open_excel
import cogs.FireBaseGestor as Datos
from threading import Thread, Timer
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

    async def quitarsilencio(self, person, silencio, tiempo):
        """Esta función administra el tiempo que un usuario estará con el role
        de silencio (Le agrega el role y también se lo quita)"""

        if silencio != None:
            await person.add_roles(silencio)
            await sleep(tiempo)
            await person.remove_roles(silencio)
            try:
                await person.edit(mute=False)
            except discord.errors.HTTPException:
                pass
        else:
            await sleep(tiempo)
            try:
                await person.edit(mute=False)
            except discord.errors.HTTPException:
                pass

    async def quitarban(self, person, tiempo):
        """Esta función administra el tiempo que un usuario estará baneado
        de un server"""

        try:
            await person.ban()
            await sleep(tiempo)
            await person.unban()
        except:
            pass

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

    async def cast_apl(self, server, person, fecha, idioma):
        database = Datos.alldata()
        memberdata = Datos.memberdata(server, str(person.id))
        castigo_aplicar = None
        index_castigo = 0
        for castigo in database["servers"][server]["configs"]["castigos"]:
            if castigo["cant_warns"] <= len(memberdata["avisado"]):
                apl_castigo = True
                if "cast_apl" in memberdata["avisado"][len(memberdata["avisado"]) - castigo["cant_warns"]]:
                    for castigo_apl in memberdata["avisado"][len(memberdata["avisado"]) - castigo["cant_warns"]]["cast_apl"]:
                        if int(castigo_apl) == index_castigo:
                            apl_castigo = False
                if apl_castigo:
                    fecha_ver = fecha - timedelta(castigo["dias"])
                    aviso_ver = memberdata["avisado"][len(memberdata["avisado"]) - castigo["cant_warns"]]["fecha"]
                    fecha_ver2 = datetime.strptime(aviso_ver, "%d/%m/%Y")

                    if (fecha_ver - fecha_ver2.date()).days <= 0:
                        castigo_aplicar = castigo
                    if index_castigo+1 == len(database["servers"][server]["configs"]["castigos"]):
                        if castigo_aplicar != None:

                            canal = None
                            if "canal_moderacion" in database["servers"][server]["configs"]:
                                try:
                                    canal = bot.get_channel(int(database["servers"][server]["configs"]["canal_moderacion"]))
                                except discord.NotFound:
                                    Datos.delconfig(server, "canal_moderacion")

                            for x in range(castigo_aplicar["cant_warns"]):
                                if not "cast_apl" in memberdata["avisado"][len(memberdata["avisado"])-1-x]:
                                    memberdata["avisado"][len(memberdata["avisado"])-1-x]["cast_apl"] = []
                                memberdata["avisado"][len(memberdata["avisado"])-1-x]["cast_apl"].append(str(index_castigo))

                            Datos.miembro(server, str(person.id), memberdata)

                            cant = castigo_aplicar['cant_warns']
                            tiempo = castigo_aplicar["dias"]
                            razon = bot_i.cell_value(53, idioma).replace("{cant}", f"{cant}")
                            razon = razon.replace("{tiempo}", f"{tiempo}")
                            razon = razon.replace("{medida}", "días")

                            if "temp_mute" in castigo_aplicar:
                                silencio = None
                                if "role_silencio" in database["servers"][server]["configs"]:
                                    try:
                                        silencio = discord.utils.get(person.guild.roles, id=int(database["servers"][server]["configs"]["role_silencio"]))
                                    except discord.NotFound:
                                        Datos.delconfig(server, "role_silencio")

                                    if canal != None:
                                        mod_embed = embeds.embed_moderador("<@!730804779021762561>", person, razon, server, 45, idioma)
                                        await canal.send(embed=mod_embed)

                                tiempo = 60 * castigo_aplicar["tiempo"]
                                await quitarsilencio(person, silencio, tiempo)
                            elif "temp_ban" in castigo_aplicar:
                                tiempo = 60 * castigo_aplicar["tiempo"]
                                await quitarban(person, tiempo)
                            elif "expulsar" in castigo_aplicar:
                                await person.kick()
                            else:
                                await person.ban()
                        break
            index_castigo+=1

def setup(bot):
    bot.add_cog(ModeracionCommands(bot))
