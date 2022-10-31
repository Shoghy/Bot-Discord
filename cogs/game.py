import discord
from discord.ext import commands
from random import randint
from asyncio import sleep
from xlrd import open_workbook as open_excel
import cogs.FireBaseGestor as Datos

excel = open_excel("cogs\\idiomas.xlsx")
bot_i = excel.sheet_by_name("bot")
obj_i = excel.sheet_by_name("objetos")
desc_i = excel.sheet_by_name("descripciones")
mons_i = excel.sheet_by_name("monstruos")
areas_i = excel.sheet_by_name("areas")

class GameCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

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

    async def delreact(self, canal : int, usuario : int, mensaje : int, emoji=None, todo : bool=False):
        try:
            channel = self.bot.get_channel(canal)
            message = await channel.fetch_message(mensaje)
            user = self.bot.get_user(usuario)
            if todo:
                await message.clear_reactions()
            else:
                if emoji != None:
                    await message.remove_reaction(emoji, user)
                else:
                    print("Wey, no me mandaste el emoji que tengo que borrar\ngame.py\nFunción: delreact\nLinea: 74")
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
        database = Datos.alldata()
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
        adver = await ctx.send(f'{ctx.author.mention} {bot_i.cell_value(17, idioma)}')
        await sleep(3)
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
        adver = await ctx.send(f'{ctx.author.mention} {bot_i.cell_value(16, idioma)}')
        await sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass

    def niveles_habla(self, database, miembro, server):
        if not miembro in database["servers"][server]["miembros"]:
            database["servers"][server]["miembros"][miembro] = {"nivel": 1, "xp":0, "nxtniv": 100}
        return database

    #Comando que inicializa al usuario
    @commands.command(aliases=['comenzar', 'start', 'iniciar'])
    async def empezar(self, ctx):
        server = str(ctx.message.guild.id)
        database = Datos.alldata()
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permisoparajugar(str(ctx.message.channel.id), server):
            miembro = str(ctx.author.id)
            database = self.niveles_habla(database, miembro, server)
            if "juego" in database["servers"][server]["miembros"][miembro]:
                await ctx.send(f'{ctx.author.mention} {bot_i.cell_value(14, idioma)}')
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
                Datos.miembro(server, miembro, juego)
                await ctx.send(f'{ctx.author.mention} {bot_i.cell_value(15, idioma)}')
        else:
            await self.error_02(idioma, ctx)

    #Comando que muestra el inventario del usuario
    @commands.command(aliases=['inv', 'objetos', 'objs', "inventory", "items"])
    async def inventario(self, ctx):
        server = str(ctx.message.guild.id)
        database = Datos.alldata()
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permisoparajugar(str(ctx.message.channel.id), server):
            miembro = str(ctx.author.id)
            database = self.niveles_habla(database, miembro, server)
            if "juego" in database["servers"][server]["miembros"][miembro]:
                inv = self.visualizainv(database, server, miembro)
                inven = discord.Embed(
                    title=bot_i.cell_value(18, idioma),
                    description=inv,
                    color = discord.Colour.blue()
                )
                await ctx.send(f'{ctx.author.mention}',embed=inven)
            else:
                await self.error_01(idioma, ctx)
        else:
            await self.error_02(idioma, ctx)
    
    #Comando que muestra la estadística del usuario 
    @commands.command(aliases=['estadisticas', 'estadísticas', 'est', 'stat'])
    async def stats(self, ctx):
        server = str(ctx.message.guild.id)
        database = Datos.alldata()
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permisoparajugar(str(ctx.message.channel.id), server):
            miembro = str(ctx.author.id)
            database = self.niveles_habla(database, miembro, server)
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
                    url=ctx.author.avatar_url
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
                await ctx.send(f'{ctx.author.mention}', embed=std)
            else:
                await self.error_01(idioma, ctx)
        else:
            await self.error_02(idioma, ctx)
    
    @commands.command(aliases=['explore', 'aventura', 'adventure'])
    async def explorar(self, ctx):
        if self.permisoparajugar(str(ctx.message.channel.id), str(ctx.message.guild.id)):
            server = str(ctx.message.guild.id)
            database = Datos.alldata()
            miembro = str(ctx.author.id)
            idioma = database["servers"][server]["configs"]["idioma"]

            database = self.niveles_habla(database, miembro, server)

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
                                    Datos.deldbmensaje(server, msj)
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
                        mensaje = await ctx.send(f'{ctx.author.mention}', embed=areas_explo)
                        for reacciones in reacts:
                            await mensaje.add_reaction(reacciones)
                        mensaje_d = {}
                        mensaje_d["reacts"] = reacts
                        mensaje_d["miembro"] = miembro
                        mensaje_d["categoria"] = "e"
                        mensaje_d["procesando"] = False
                        mensaje_d["canal"] = str(mensaje.channel.id)
                        Datos.mensaje(server, str(mensaje.id), mensaje_d)
                        try:
                            await ctx.message.delete()
                        except discord.NotFound:
                            pass
                    
                    #Si tu hp = 0
                    else:
                        await ctx.send(f'{ctx.author.mention} {bot_i.cell_value(30, idioma)}')

                #Sí ya estás luchando contra algo
                else:
                    adver = await ctx.send(f'{ctx.author.mention} {bot_i.cell_value(29, idioma)}')
                    await sleep(2)
                    try:
                        await adver.edit(content=f"{ctx.author.mention} {bot_i.cell_value(32, idioma)}")
                        adver_msg = {}
                        adver_msg["miembro"] = miembro
                        adver_msg["categoria"] = "pr"
                        Datos.mensaje(server, str(adver.id), adver_msg)
                        await adver.add_reaction("✅")
                        await adver.add_reaction("❌")
                    except discord.NotFound:
                            pass
            else:
                await self.error_01(idioma, ctx)
        else:
            await self.error_02(idioma, ctx)

    @commands.command(aliases=['sleep', 'rest'])
    async def descansar(self, ctx):
        server = str(ctx.message.guild.id)
        database = Datos.alldata()
        idioma = database["servers"][server]["configs"]["idioma"]
        if self.permisoparajugar(str(ctx.message.channel.id), server):
            miembro = str(ctx.author.id)
            database = self.niveles_habla(database, miembro, server)
            if "juego" in database["servers"][server]["miembros"][miembro]:
                juego = database["servers"][server]["miembros"][miembro]
                if juego["juego"]["luchando"] == "nada":
                    juego["juego"]["dinero"] -= 3
                    if juego["juego"]["dinero"] < 0:
                        juego["juego"]["dinero"] = 0
                    juego["juego"]["hp"] = juego["juego"]["maxhp"]
                    Datos.miembro(server, miembro, juego)
                    await ctx.send(f'{ctx.author.mention} {bot_i.cell_value(34, idioma)}')
                else:
                    await ctx.send(f'{ctx.author.mention} {bot_i.cell_value(33, idioma)}')
            else:
                await self.error_01(idioma, ctx)
        else:
            await self.error_02(idioma, ctx)
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        database = Datos.alldata()
        server = str(reaction.guild_id)
        msj = str(reaction.message_id)
        if msj in database["servers"][server]["mensajes"]:
            idioma = database["servers"][server]["configs"]["idioma"]
            miembro = str(reaction.user_id)
            if miembro != "730804779021762561" and miembro != "736966021528944720":
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
                            Datos.mensaje(server, msj, mensaje_d)

                            #Explorar
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
                                await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, todo=True)
                                juego = database["servers"][server]["miembros"][miembro]
                                juego["juego"]["luchando"] = luchando
                                mensaje_d["categoria"] = "l"
                                mensaje_d["reacts"] = {"🔪":"atacar", "💨":"huir"}
                                mensaje_d["procesando"] = False
                                mongrafichp = self.porvida(luchando["hp"], luchando["maxhp"])
                                playerhp = self.porvida(juego["juego"]["hp"], juego["juego"]["maxhp"])
                                lucha = discord.Embed(
                                    title=f"{bot_i.cell_value(7, idioma)} **{mons_i.cell_value(id_mons, idioma)}**",
                                    description=f"{bot_i.cell_value(10, idioma)}:{playerhp}{juego['juego']['hp']}/{juego['juego']['maxhp']}\n{mons_i.cell_value(id_mons, idioma)}:{mongrafichp}",
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
                                        Datos.deldbmensaje(server, msj)
                                        return
                                for react in mensaje_d["reacts"]:
                                    await mensaj.add_reaction(react)
                                await self.delreact(mensaj.channel.id, mensaj.author.id, mensaj.id, emoji)
                                Datos.mensaje(server, msj, mensaje_d)
                                Datos.miembro(server, miembro, juego)

                            #Lucha
                            """elif mensaje_d["categoria"] == "l":
                                for react in mensaje_d["reacts"]:
                                    await self.delreact(reaction.channel_id, 736966021528944720, reaction.message_id, react)
                                await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                                if accion == "atacar":
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
                                            await sleep(2)
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
                                        await sleep(2)
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
                                        await sleep(2)
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
                        else:
                            await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                    else:
                        await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)

def setup(bot):
    bot.add_cog(GameCommands(bot))