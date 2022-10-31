import discord
from discord.ext import commands
import json
from random import randint
import asyncio
from xlrd import open_workbook as open_excel
from firebase import firebase

excel = open_excel("cogs\\idiomas.xlsx")
bot_i = excel.sheet_by_name("bot")
obj_i = excel.sheet_by_name("objetos")
desc_i = excel.sheet_by_name("descripciones")
mons_i = excel.sheet_by_name("monstruos")
areas_i = excel.sheet_by_name("areas")

class GameCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Devuelve los valores del archivo json
    def leerjson(self):
        conexion = firebase.FirebaseApplication("https://botcaballero-7338b.firebaseio.com/", None)
        resultado = conexion.get('', '/')
        return resultado

    #Añade los cambios al archivo json
    def escribirjson(self, data):
        conexion = firebase.FirebaseApplication("https://botcaballero-7338b.firebaseio.com/", None)
        conexion.put('', '/', data)

    #Devuelve un strings con los huecos del inventario
    def visualizainv(self, database, server : str, miembro : str):
        casillas = ":x::one: :two: :three: :four: :five: :six: :seven: :eight: :nine:\n:one:"
        inventario = database["servers"][server]["miembros"][miembro]["juego"]["inventario"]
        for i in range(27):
            if "item" in inventario[i]:
                objeto = inventario[i]["item"]
                casillas = casillas + database["objetos"][objeto]["emj_d"]+" "
            else:
                casillas = casillas + ":blue_square: "
            if i == 8:
                casillas = casillas + "\n\n:two:"
            if i == 17:
                casillas = casillas + "\n\n:three:"
        return casillas

    #Devuelve el porcentaje de la vida en 5 corazones (corazones rojos, corazones rotos y corazones negros)
    def porvida(self, vida : int, maxvida : int):
        corazones = ""
        porcvida = int(100*(vida/maxvida))
        por = 0
        while por < 100:
            por += 10
            if porcvida >= por:
                por += 10
                if porcvida >= por:
                    corazones = corazones + ":heart:"
                else:
                    corazones = corazones + ":broken_heart:"
            else:
                if por == 10 and porcvida > 0:
                    corazones = corazones + ":broken_heart:"
                else:
                    corazones = corazones + ":black_heart:"
                por += 10
        return corazones
    
    #Devuelve el daño realizado
    def dmgrealizado(self, atq : int, defe : int, prec : int):
        dmg = int(0)
        acierto = randint(1, 100)
        if acierto <= prec:
            if defe > 0:
                dmg = int(atq*((10/defe)/10))
                if (atq*((10/defe)/10)) >= dmg+0.5:
                    dmg +=1
                if dmg <= 0:
                    dmg = 1
            else:
                dmg = atq
        else:
            dmg = 0
        return dmg

    async def delreact(self, canal : int, usuario : int, mensaje : int, emoji):
        try:
            channel = self.bot.get_channel(canal)
            message = await channel.fetch_message(mensaje)
            user = self.bot.get_user(usuario)
            await message.remove_reaction(emoji, user)
        except discord.HTTPException:
            pass

    def acenemigo(self, p, idmem, idserver):
        respuesta = [1, 2, False]
        idioma = p["jugadores"][idserver]["configs"]["idioma"]
        mons = p["jugadores"][idserver][idmem]["luchando"]
        player = p["jugadores"][idserver][idmem]
        dmg = self.dmgrealizado(mons["atq"], p["jugadores"][idserver][idmem]["def"], mons["prec"])
        player["hp"] -= dmg
        if dmg > 0:
            if player["hp"] <= 0:
                respuesta[2] = True
                player["hp"] = 0
                playerhp = self.porvida(player["hp"], player["maxhp"])
                mongrafichp = self.porvida(mons["hp"], mons["maxhp"])
                a2 = discord.Embed(
                    title=f'{p["idiomas"][idioma]["luchando_contra"]} **{player["luchando"]["name"]}**',
                    color = discord.Colour.blue()
                )
                a2.add_field(
                    name=p["idiomas"][idioma]["narrador"],
                    value=f'{p["idiomas"][idioma]["perder"]} **{mons["name"]}**',
                    inline=False
                )
                p["jugadores"][idserver][idmem]["hp"] = 0
                p["jugadores"][idserver][idmem]["luchando"] = None
                respuesta[0] = p
                respuesta[1] = a2
            else:
                p["jugadores"][idserver][idmem]["hp"] = player["hp"]
                playerhp = self.porvida(player["hp"], player["maxhp"])
                mongrafichp = self.porvida(mons["hp"], mons["maxhp"])
                msg = p["idiomas"][idioma]["luchando_contra"]
                n = p["idiomas"][idioma]["tu_vida"]
                a2 = discord.Embed(
                    title=f"{msg} **{player['luchando']['name']}**",
                    description=f"{n}:{playerhp}{player['hp']}/{player['maxhp']}\n{player['luchando']['name']}:{mongrafichp}",
                    color = discord.Colour.blue()
                )
                punto = p["idiomas"][idioma]["punto"]
                if dmg > 1:
                    punto = p["idiomas"][idioma]["puntos"]
                a2.add_field(
                    name="Narrador",
                    value=f"**{mons['name']}** te ha quitado {dmg} {punto} de vida",
                    inline=False
                )
                respuesta[0] = p
                respuesta[1] = a2
        else:
            playerhp = self.porvida(player["hp"], player["maxhp"])
            mongrafichp = self.porvida(mons["hp"], mons["maxhp"])
            msg = p["idiomas"][idioma]["luchando_contra"]
            n = p["idiomas"][idioma]["tu_vida"]
            a2 = discord.Embed(
                title=f"{msg} **{player['luchando']['name']}**",
                description=f"{n}:{playerhp}{player['hp']}/{player['maxhp']}\n{player['luchando']['name']}:{mongrafichp}",
                color = discord.Colour.blue()
            )
            msg = p["idiomas"][idioma]["esquivaste"]
            n = p["idiomas"][idioma]["narrador"]
            a2.add_field(
                name=n,
                value=f"**{mons['name']}** {msg}",
                inline=False
            )
            respuesta[0] = p
            respuesta[1] = a2
        return respuesta
    
    def permisoparajugar(self, canal : str, server : str):
        permisoconcedido = False
        database = self.leerjson()
        if "juego_canales" in database["servers"][server]["configs"]:
            if canal in database["servers"][server]["configs"]["juego_canales"]:
                if database["servers"][server]["configs"]["juego_canales"][canal]:
                    permisoconcedido = True
            else:
                if database["servers"][server]["configs"]["juego_canales"]["allfalse"]:
                    permisoconcedido = True
                elif not database["servers"][server]["configs"]["juego_canales"]["alltrue"]:
                    permisoconcedido = True
        else:
            permisoconcedido = True
        return permisoconcedido

    async def error_01(self, idioma, ctx):
        """Personaje inexestente"""
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass
        adver = await ctx.send(f'{ctx.message.author.mention} {bot_i.cell_value(17, idioma)}')
        await asyncio.sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass
    
    async def error_02(self, idioma, ctx):
        """Commandos deshabilitados"""
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass
        adver = await ctx.send(f'{ctx.message.author.mention} {bot_i.cell_value(16, idioma)}')
        await asyncio.sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass

    #Comando que inicializa al usuario
    @commands.command(aliases=['comenzar', 'start', 'iniciar'])
    async def empezar(self, ctx):
        server = str(ctx.message.guild.id)
        database = self.leerjson()
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permisoparajugar(str(ctx.message.channel.id), server):
            miembro = str(ctx.message.author.id)
            if not miembro in database["servers"][server]["miembros"]:
                database["servers"][server]["miembros"][miembro] = {"nivel": 0}
            if "juego" in database["servers"][server]["miembros"][miembro]:
                await ctx.send(f'{ctx.message.author.mention} {bot_i.cell_value(14, idioma)}')
            else:
                juego = database["servers"][server]["miembros"][miembro]
                juego["juego"] = {}
                juego["juego"]["inventario"] = {}
                for i in range(27):
                    juego["juego"]["inventario"][str(i)] = ":blue_square:"
                juego["juego"]["dinero"] = 0
                juego["juego"]["nivel"] = 1
                juego["juego"]["xp"] = 0
                juego["juego"]["hp"] = 20
                juego["juego"]["maxhp"] = 20
                juego["juego"]["nxtnivel"] = 100
                juego["juego"]["atq"] = 5
                juego["juego"]["def"] = 2
                juego["juego"]["vendiendo"] = "nada"
                juego["juego"]["luchando"] = "nada"
                juego["juego"]["nsitem"] = "nada"
                juego["juego"]["arma"] = "nada"
                juego["juego"]["armadura"] = "nada"
                database["servers"][server]["miembros"][miembro] = juego
                self.escribirjson(database)
                await ctx.send(f'{ctx.message.author.mention} {bot_i.cell_value(15, idioma)}')
        else:
            await self.error_02(idioma, ctx)

    #Comando que muestra el inventario del usuario
    @commands.command(aliases=['inv', 'objetos', 'objs', "inventory", "items"])
    async def inventario(self, ctx):
        server = str(ctx.message.guild.id)
        database = self.leerjson()
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permisoparajugar(str(ctx.message.channel.id), server):
            miembro = str(ctx.message.author.id)
            if not miembro in database["servers"][server]["miembros"]:
                database["servers"][server]["miembros"][miembro] = {"nivel": 0}
            if "juego" in database["servers"][server]["miembros"][miembro]:
                inv = self.visualizainv(database, server, miembro)
                inven = discord.Embed(
                    title=bot_i.cell_value(18, idioma),
                    description=inv,
                    color = discord.Colour.blue()
                )
                await ctx.send(f'{ctx.message.author.mention}',embed=inven)
            else:
                await self.error_01(idioma, ctx)
        else:
            await self.error_02(idioma, ctx)
    
    #Comando que muestra la estadística del usuario 
    @commands.command(aliases=['estadisticas', 'estadísticas', 'est', 'stat'])
    async def stats(self, ctx):
        server = str(ctx.message.guild.id)
        database = self.leerjson()
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permisoparajugar(str(ctx.message.channel.id), server):
            miembro = str(ctx.message.author.id)
            if not miembro in database["servers"][server]["miembros"]:
                database["servers"][server]["miembros"][miembro] = {"nivel": 0}
            if "juego" in database["servers"][server]["miembros"][miembro]:
                #variable que separa los datos del jugador de todos los demás
                juego = database["servers"][server]["miembros"][miembro]["juego"]

                vida = self.porvida(juego["hp"], juego["maxhp"])
                arma = [bot_i.cell_value(19, idioma), ""]
                armadura = [bot_i.cell_value(19, idioma), ""]
                
                if juego["arma"] != "nada":
                    arma[0] = obj_i.cell_value(juego["arma"]["id"], idioma)
                    arma[1] = database["objetos"][str(juego["arma"]["id"])]["emj_d"]
                if juego["armadura"] != "nada":
                    armadura[0] = obj_i.cell_value(juego["armadura"]["id"], idioma)
                    armadura[1] = database["objetos"][str(juego["armadura"]["id"])]["emj_d"]
                std = discord.Embed(
                    title=bot_i.cell_value(20, idioma),
                    color = discord.Colour.blue()
                )
                std.set_thumbnail(
                    url=ctx.message.author.avatar_url
                )
                std.add_field(
                    name=bot_i.cell_value(21, idioma),
                    value=f':gear:{juego["nivel"]}',
                    inline=False
                )
                std.add_field(
                    name="HP",
                    value=vida+f'\n{juego["hp"]}/{juego["maxhp"]}',
                    inline=False
                )
                std.add_field(
                    name=bot_i.cell_value(22, idioma),
                    value=f':crossed_swords:{juego["atq"]}',
                    inline=False
                )
                std.add_field(
                    name=bot_i.cell_value(23, idioma),
                    value=f':shield:{juego["def"]}',
                    inline=False
                )
                std.add_field(
                    name=bot_i.cell_value(24, idioma),
                    value=f'{arma[1]}{arma[0]}',
                    inline=False
                )
                std.add_field(
                    name=bot_i.cell_value(25, idioma),
                    value=f'{armadura[1]}{armadura[0]}',
                    inline=False
                )
                std.add_field(
                    name=bot_i.cell_value(26, idioma),
                    value=f'{juego["xp"]}/{juego["nxtnivel"]}',
                    inline=False
                )
                std.add_field(
                    name=bot_i.cell_value(27, idioma),
                    value=f':moneybag:{juego["dinero"]}',
                    inline=False
                )
                await ctx.send(f'{ctx.message.author.mention}', embed=std)
            else:
                await self.error_01(idioma, ctx)
        else:
            await self.error_02(idioma, ctx)
    
    @commands.command()
    async def explorar(self, ctx):
        if self.permisoparajugar(str(ctx.message.channel.id), str(ctx.message.guild.id)):
            server = str(ctx.message.guild.id)
            database = self.leerjson()
            miembro = str(ctx.message.author.id)
            idioma = database["servers"][server]["configs"]["idioma"]

            if not miembro in database["servers"][server]["miembros"]:
                database["servers"][server]["miembros"][miembro] = {"nivel": 0}

            if "juego" in database["servers"][server]["miembros"][miembro]:
                juego = database["servers"][server]["miembros"][miembro]["juego"]
                if juego["luchando"] == "nada":
                    if juego["hp"] > 0:
                        for msj in database["servers"][server]["mensajes"]:
                            if msj != "ddf":
                                if database["servers"][server]["mensajes"][msj]["miembro"] == miembro and database["servers"][server]["mensajes"][msj]["categoria"] == "e":
                                    try:
                                        canal = self.bot.get_channel(int(database["servers"][server]["mensajes"][msj]["canal"]))
                                        if canal != None:
                                            mensaj = await canal.fetch_message(int(msj))
                                            await mensaj.delete()
                                    except discord.NotFound:
                                        pass
                                    del database["servers"][server]["mensajes"][msj]
                                    break
                        descareas = ""
                        reacts = {}
                        for area in range(len(database["areas"])):
                            if area != 0:
                                if juego["nivel"] >= database["areas"][int(area)]["minnv"]:
                                    if descareas == "":
                                        descareas =f"{database['areas'][area]['react']}**"+areas_i.cell_value(area, idioma)+"**"
                                    else:
                                        descareas = descareas+"\n"+f"{database['areas'][area]['react']}**"+areas_i.cell_value(area, idioma)+"**"
                                    reacts[database["areas"][area]["react"]] = area
                                    if juego["nivel"] <= database["areas"][area]["minnv"]:
                                        break
                        areas_explo = discord.Embed(
                            title=bot_i.cell_value(31, idioma),
                            description=descareas+"\n*Elige un area*",
                            color = discord.Colour.blue()
                        )
                        mensaje = await ctx.send(f'{ctx.message.author.mention}', embed=areas_explo)
                        for reacciones in reacts:
                            await mensaje.add_reaction(reacciones)
                        mensaje_d = database["servers"][server]["mensajes"]
                        mensaje_d[str(mensaje.id)] = {}
                        mensaje_d[str(mensaje.id)]["reacts"] = reacts
                        mensaje_d[str(mensaje.id)]["miembro"] = miembro
                        mensaje_d[str(mensaje.id)]["categoria"] = "e"
                        mensaje_d[str(mensaje.id)]["procesando"] = False
                        mensaje_d[str(mensaje.id)]["canal"] = str(mensaje.channel.id)
                        database["servers"][server]["mensajes"] = mensaje_d
                        self.escribirjson(database)
                        try:
                            await ctx.message.delete()
                        except discord.NotFound:
                            pass
                    
                    #Si tu hp = 0
                    else:
                        await ctx.send(f'{ctx.message.author.mention} {bot_i.cell_value(30, idioma)}')

                #Sí ya estás luchando contra algo
                else:
                    adver = await ctx.send(f'{ctx.message.author.mention} {bot_i.cell_value(29, idioma)}')
                    await asyncio.sleep(3)
                    try:
                        adver.edit(f'{ctx.message.author.mention} {bot_i.cell_value(32, idioma)}')
                        database["servers"][server]["mensajes"][str(adver.id)] = {}
                        database["servers"][server]["mensajes"][str(adver.id)]["miembro"] = miembro
                        database["servers"][server]["mensajes"][str(adver.id)]["categoria"] = "pr"
                        self.escribirjson(database)
                        await adver.add_reaction("✅")
                        await adver.add_reaction("❌")
                    except discord.NotFound:
                            pass
            else:
                await self.error_01(idioma, ctx)
        else:
            await self.error_02(idioma, ctx)

    @commands.command()
    async def descansar(self, ctx):
        server = str(ctx.message.guild.id)
        database = self.leerjson()
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permisoparajugar(str(ctx.message.channel.id), server):
            miembro = str(ctx.message.author.id)
            if not miembro in database["servers"][server]["miembros"]:
                database["servers"][server]["miembros"][miembro] = {"nivel": 0}
            if "juego" in database["servers"][server]["miembros"][miembro]:
                juego = database["servers"][server]["miembros"][miembro]["juego"]
                if juego["luchando"] == "nada":
                    juego["dinero"] -= 3
                    if juego["dinero"] < 0:
                        juego["dinero"] = 0
                    juego["hp"] = juego["maxhp"]
                    database["servers"][server]["miembros"][miembro]["juego"] = juego
                    self.escribirjson(database)
                    await ctx.send(f'{ctx.message.author.mention} {bot_i.cell_value(34, idioma)}')
                else:
                    await ctx.send(f'{ctx.message.author.mention} {bot_i.cell_value(33, idioma)}')
            else:
                await self.error_01(idioma, ctx)
        else:
            await self.error_02(idioma, ctx)
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        server = str(reaction.guild_id)
        database = self.leerjson()
        idioma = database["servers"][server]["configs"]["idioma"]
        miembro = str(reaction.user_id)
        msj = str(reaction.message_id)
        if miembro != "730804779021762561" and miembro != "736966021528944720":
            if msj in database["servers"][server]["mensajes"]:
                mensaje_d = database["servers"][server]["mensajes"][msj]
                emoji = None
                if reaction.emoji.id == None:
                    emoji = f"{reaction.emoji.name}"
                else:
                    emoji = self.bot.get_emoji(reaction.emoji.id)
                if miembro != mensaje_d["miembro"]:
                    await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                else:
                    z = False
                    accion = None
                    for react in mensaje_d["reacts"]:
                        if react == emoji:
                            z = True
                            accion = mensaje_d["reacts"][react]
                            break
                    if z:
                        if not mensaje_d["procesando"]:
                            mensaje_d["procesando"] = True
                            database["servers"][server]["mensajes"][msj] = mensaje_d
                            self.escribirjson(database)
                            if mensaje_d["categoria"] == "e":
                                area = database["areas"][accion]
                                namon = randint(1, area["mons_cant"])
                                itemdrop = randint(1, 100)
                                dinerodrop = randint(area["monstruos"][namon]["mindinero"], area["monstruos"][namon]["maxdinero"])
                                nivel = randint(area["monstruos"][namon]["minlevel"], area["monstruos"][namon]["maxlevel"])
                                id_mons = area["monstruos"][namon]["id_mons"]
                                if itemdrop <= area["monstruos"][namon]["objeto1"]["prob"]:
                                    itemdrop = area["monstruos"][namon]["objeto1"]["id"]
                                elif itemdrop <= area["monstruos"][namon]["objeto2"]["prob"]:
                                    itemdrop = area["monstruos"][namon]["objeto2"]["id"]
                                else:
                                    itemdrop = area["monstruos"][namon]["objeto3"]["id"]
                                monstruo = database["monstruos"][id_mons]
                                luchando = {
                                    "id_mons": id_mons,
                                    "area": accion,
                                    "nivel": nivel+1,
                                    "atq": monstruo["atqbase"] + int(nivel * 1.5),
                                    "hp": monstruo["hpbase"] + (nivel*2),
                                    "maxhp": monstruo["hpbase"] + (nivel*2),
                                    "def": monstruo["defbase"] + nivel,
                                    "prec": monstruo["prec"],
                                    "xp": monstruo["xpbase"] + nivel,
                                    "drop": itemdrop,
                                    "dinero": dinerodrop
                                }
                                for react in mensaje_d["reacts"]:
                                    #id del bot de pruebas
                                    await self.delreact(reaction.channel_id, 736966021528944720, reaction.message_id, react)
                                await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                                juego = database["servers"][server]["miembros"][miembro]["juego"]
                                juego["luchando"] = luchando
                                mensaje_d["categoria"] = "l"
                                mensaje_d["reacts"] = {"🔪":"atacar", "💨":"huir"}
                                mensaje_d["procesando"] = False
                                mongrafichp = self.porvida(luchando["hp"], luchando["maxhp"])
                                playerhp = self.porvida(juego["hp"], juego["maxhp"])
                                lucha = discord.Embed(
                                    title=f"{bot_i.cell_value(7, idioma)} **{mons_i.cell_value(id_mons, idioma)}**",
                                    description=f"{bot_i.cell_value(10, idioma)}:{playerhp}{juego['hp']}/{juego['maxhp']}\n{mons_i.cell_value(id_mons, idioma)}:{mongrafichp}",
                                    color = discord.Colour.blue()
                                )
                                lucha.add_field(
                                    name=f"{bot_i.cell_value(8, idioma)}",
                                    value=f"**{mons_i.cell_value(id_mons, idioma)}** {bot_i.cell_value(38, idioma)}",
                                    inline=False
                                )
                                mensaj = None
                                try:
                                    canal = self.bot.get_channel(reaction.channel_id)
                                    mensaj = await canal.fetch_message(reaction.message_id)
                                    await mensaj.edit(embed=lucha)
                                except discord.HTTPException:
                                    try:
                                        canal = self.bot.get_channel(reaction.channel_id)
                                        mensaj = await canal.send("{reaction.member.mention}", embed=lucha)
                                    except discord.HTTPException:
                                        if reaction.member.dm_channel != None:
                                            men_dir = await reaction.member.dm_channel
                                            server_name = self.bot.get_guild(int(server)).name
                                            await men_dir.send(f"{bot_i.cell_value(35, idioma)}\n\n**{bot_i.cell_value(36, idioma)}:**{server_name}\n\n{bot_i.cell_value(37, idioma)}")
                                        else:
                                            men_dir = await reaction.member.create_dm()
                                            server_name = self.bot.get_guild(int(server)).name
                                            await men_dir.send(f"{bot_i.cell_value(35, idioma)}\n\n**{bot_i.cell_value(36, idioma)}:**{server_name}\n\n{bot_i.cell_value(37, idioma)}")
                                        del database["servers"][server]["mensajes"][msj]
                                        self.escribirjson(database)
                                        return
                                for react in mensaje_d["reacts"]:
                                    await mensaj.add_reaction(react)
                                await self.delreact(mensaj.channel.id, mensaj.author.id, mensaj.id, emoji)
                                database["servers"][server]["mensajes"][msj] = mensaje_d
                                database["servers"][server]["miembros"][miembro]["juego"] = juego
                            """elif p["mensajes"][idserver][str(reaction.message_id)]["categoria"] == "l":
                                for react in p["mensajes"][idserver][str(reaction.message_id)]["reacts"]:
                                    await self.delreact(reaction.channel_id, 736966021528944720, reaction.message_id, react)
                                await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                                if p["mensajes"][idserver][str(reaction.message_id)]["acciones"][indice] == "atacar":
                                    player = p["jugadores"][idserver][idmem]
                                    prec = 95
                                    if player["arma"] != None:
                                        prec = p["objetos"][player["arma"]]["prec"]
                                    dmg = self.dmgrealizado(player["atq"], player["luchando"]["def"], prec)
                                    if dmg > 0:
                                        player["luchando"]["hp"] -= dmg
                                        if player["luchando"]["hp"] <= 0:
                                            win = discord.Embed(
                                                title=f"Le has ganado al **{player['luchando']['name']}**",
                                                color = discord.Colour.blue()
                                            )
                                            p["jugadores"][idserver][idmem]["dinero"] += player['luchando']['dinero']
                                            p["jugadores"][idserver][idmem]["xp"] += player['luchando']['xp']
                                            noguardado = True
                                            for a in range(27):
                                                a1 = str(a)
                                                if player["slot"][a1] == ":blue_square:":
                                                    p["jugadores"][idserver][idmem]["slot"][a1] = {}
                                                    p["jugadores"][idserver][idmem]["slot"][a1]["item"] = player['luchando']['drop']
                                                    p["jugadores"][idserver][idmem]["slot"][a1]["cant"] = 1
                                                    noguardado = False
                                                    break
                                                elif "item" in player["slot"][a1]:
                                                    if player["slot"][a1]["item"] == player['luchando']['drop'] and player["slot"][a1]["cant"] < p["objetos"][player['luchando']['drop']]["max"]:
                                                        p["jugadores"][idserver][idmem]["slot"][a1]["cant"] += 1
                                                        noguardado = False
                                                        break
                                            if noguardado:
                                                win.add_field(
                                                    name="Ganancias",
                                                    value=f"Dinero: :moneybag:{player['luchando']['dinero']}\nObjeto: **Inventario lleno**\nXP: {player['luchando']['xp']}",
                                                    inline=False
                                                )
                                            else:
                                                win.add_field(
                                                    name="Ganancias",
                                                    value=f"Dinero: :moneybag:{player['luchando']['dinero']}\nObjeto: {p['objetos'][player['luchando']['drop']]['emj_d']}{player['luchando']['drop'].capitalize()}\nXP: {player['luchando']['xp']}",
                                                    inline=False
                                                )
                                            await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                                            canal = self.bot.get_channel(reaction.channel_id)
                                            mensaj = await canal.fetch_message(reaction.message_id)
                                            del p['mensajes'][idserver][str(reaction.message_id)]
                                            p["jugadores"][idserver][idmem]["luchando"] = None
                                            await mensaj.edit(embed=win)
                                        else:
                                            playerhp = self.porvida(player["hp"], player["maxhp"])
                                            mongrafichp = self.porvida(player["luchando"]["hp"], player["luchando"]["maxhp"])
                                            lucha = discord.Embed(
                                                title=f"Luchando contra **{player['luchando']['name']}**",
                                                description=f"Tu vida:{playerhp}{player['hp']}/{player['maxhp']}\n{player['luchando']['name']}:{mongrafichp}",
                                                color = discord.Colour.blue()
                                            )
                                            pn = "punto"
                                            if dmg > 1:
                                                pn = "puntos"
                                            lucha.add_field(
                                                name="Narrador",
                                                value=f"Le has quitado {dmg} {pn} de vida a **{player['luchando']['name']}**",
                                                inline=False
                                            )
                                            p["jugadores"][idserver][idmem]["luchando"]["hp"] = player["luchando"]["hp"]
                                            canal = self.bot.get_channel(reaction.channel_id)
                                            mensaj = await canal.fetch_message(reaction.message_id)
                                            await mensaj.edit(embed=lucha)
                                            await asyncio.sleep(2)
                                            enenm = self.acenemigo(p, idmem, idserver)
                                            p = enenm[0]
                                            await mensaj.edit(embed=enenm[1])
                                            if enenm[2]:
                                                del p["mensajes"][idserver][str(reaction.message_id)]
                                            else:
                                                p["mensajes"][idserver][str(reaction.message_id)]["procesando"] = False
                                                for react in p["mensajes"][idserver][str(reaction.message_id)]["reacts"]:
                                                    channel = self.bot.get_channel(reaction.channel_id)
                                                    mensaje = await channel.fetch_message(reaction.message_id)
                                                    await mensaje.add_reaction(react)
                                    else:
                                        mongrafichp = self.porvida(player["luchando"]["hp"], player["luchando"]["maxhp"])
                                        playerhp = self.porvida(player["hp"], player["maxhp"])
                                        lucha = discord.Embed(
                                            title=f"Luchando contra **{player['luchando']['name']}**",
                                            description=f"Tu vida:{playerhp}{player['hp']}/{player['maxhp']}\n{player['luchando']['name']}:{mongrafichp}",
                                            color = discord.Colour.blue()
                                        )
                                        lucha.add_field(
                                            name="Narrador",
                                            value=f"No lograste golpear a **{player['luchando']['name']}**",
                                            inline=False
                                        )
                                        canal = self.bot.get_channel(reaction.channel_id)
                                        mensaj = await canal.fetch_message(reaction.message_id)
                                        await mensaj.edit(embed=lucha)
                                        await asyncio.sleep(2)
                                        enenm = self.acenemigo(p, idmem, idserver)
                                        p = enenm[0]
                                        await mensaj.edit(embed=enenm[1])
                                        if enenm[2]:
                                            del p["mensajes"][idserver][str(reaction.message_id)]
                                        else:
                                            p["mensajes"][idserver][str(reaction.message_id)]["procesando"] = False
                                            for react in p["mensajes"][idserver][str(reaction.message_id)]["reacts"]:
                                                channel = self.bot.get_channel(reaction.channel_id)
                                                mensaje = await channel.fetch_message(reaction.message_id)
                                                await mensaje.add_reaction(react)
                                elif p["mensajes"][idserver][str(reaction.message_id)]["acciones"][indice] == "escapar":
                                    intento = randint(1, 100)
                                    if intento > 50:
                                        for react in p["mensajes"][idserver][str(reaction.message_id)]["reacts"]:
                                            await self.delreact(reaction.channel_id, 736966021528944720, reaction.message_id, react)
                                        del p["mensajes"][idserver][str(reaction.message_id)]
                                        escape = discord.Embed(
                                            title="Escape",
                                            color = discord.Colour.blue()
                                        )
                                        escape.add_field(
                                            name="Narrador",
                                            value="Escapaste con éxito del combate",
                                            inline=False
                                        )
                                        p["jugadores"][idserver][idmem]["luchando"] = None
                                        canal = self.bot.get_channel(reaction.channel_id)
                                        mensaj = await canal.fetch_message(reaction.message_id)
                                        await mensaj.edit(embed=escape)
                                    else:
                                        escape = discord.Embed(
                                            title="Escape",
                                            color = discord.Colour.blue()
                                        )
                                        escape.add_field(
                                            name="Narrador",
                                            value="No lograste escapar del combate",
                                            inline=False
                                        )
                                        canal = self.bot.get_channel(reaction.channel_id)
                                        mensaj = await canal.fetch_message(reaction.message_id)
                                        await mensaj.edit(embed=escape)
                                        await asyncio.sleep(2)
                                        enenm = self.acenemigo(p, idmem, idserver)
                                        p = enenm[0]
                                        await mensaj.edit(embed=enenm[1])
                                        if enenm[2]:
                                            del p["mensajes"][idserver][str(reaction.message_id)]
                                        else:
                                            p["mensajes"][idserver][str(reaction.message_id)]["procesando"] = False
                                            for react in p["mensajes"][idserver][str(reaction.message_id)]["reacts"]:
                                                channel = self.bot.get_channel(reaction.channel_id)
                                                mensaje = await channel.fetch_message(reaction.message_id)
                                                await mensaje.add_reaction(react)"""
                            self.escribirjson(database)
                        else:
                            await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                    else:
                        await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)

def setup(bot):
    bot.add_cog(GameCommands(bot))