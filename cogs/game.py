import discord
from discord.ext import commands
import json
from random import randint
import asyncio

class GameCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Devuelve los valores del archivo json
    def leerjson(self):
        jugador = None
        with open("cogs/personajes.json", 'r', encoding="utf-8") as contenido:
            jugador = json.load(contenido)
        return jugador

    #Añade los cambios al archivo json
    def escribirjson(self, jugador):
        with open("cogs/personajes.json", 'w', encoding="utf-8") as contenido:
            json.dump(jugador, contenido)

    #Devuelve un strings con los huecos del inventario
    def visualizainv(self, jugador, idmem : str):
        casillas = ":x::one: :two: :three: :four: :five: :six: :seven: :eight: :nine:\n:one:"
        for i in range(27):
            if "item" in jugador["jugadores"][idmem]["slot"][str(i)]:
                objeto = jugador["jugadores"][idmem]["slot"][str(i)]["item"]
                casillas = casillas + jugador["objetos"][objeto]["emj_d"]+" "
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
        channel = self.bot.get_channel(canal)
        message = await channel.fetch_message(mensaje)
        user = self.bot.get_user(usuario)
        await message.remove_reaction(emoji, user)
    
    def acenemigo(self, p, idmem):
        respuesta = [1, 2, False]
        mons = p["jugadores"][idmem]["luchando"]
        player = p["jugadores"][idmem]
        dmg = self.dmgrealizado(mons["atq"], p["jugadores"][idmem]["def"], mons["prec"])
        player["hp"] -= dmg
        if dmg > 0:
            if player["hp"] <= 0:
                respuesta[2] = True
                player["hp"] = 0
                playerhp = self.porvida(player["hp"], player["maxhp"])
                mongrafichp = self.porvida(mons["hp"], mons["maxhp"])
                a2 = discord.Embed(
                    title=f"Luchando contra {player['luchando']['n']} **{player['luchando']['name']}**",
                    color = discord.Colour.blue()
                )
                a2.add_field(
                    name="Narrador",
                    value=f"Has perdido contra **{mons['name']}**",
                    inline=False
                )
                p["jugadores"][idmem]["hp"] = 0
                p["jugadores"][idmem]["luchando"] = None
                respuesta[0] = p
                respuesta[1] = a2
            else:
                p["jugadores"][idmem]["hp"] = player["hp"]
                playerhp = self.porvida(player["hp"], player["maxhp"])
                mongrafichp = self.porvida(mons["hp"], mons["maxhp"])
                a2 = discord.Embed(
                    title=f"Luchando contra {player['luchando']['n']} **{player['luchando']['name']}**",
                    description=f"Tu vida:{playerhp}{player['hp']}/{player['maxhp']}\n{player['luchando']['name']}:{mongrafichp}",
                    color = discord.Colour.blue()
                )
                punto = "punto"
                if dmg > 1:
                    punto = "puntos"
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
            a2 = discord.Embed(
                title=f"Luchando contra {player['luchando']['n']} **{player['luchando']['name']}**",
                description=f"Tu vida:{playerhp}{player['hp']}/{player['maxhp']}\n{player['luchando']['name']}:{mongrafichp}",
                color = discord.Colour.blue()
            )
            a2.add_field(
                name="Narrador",
                value=f"**{mons['name']}** ha fallado su ataque",
                inline=False
            )
            respuesta[0] = p
            respuesta[1] = a2
        return respuesta

    #Comando que inicializa al usuario
    @commands.command(aliases=['comenzar', 'start', 'iniciar'])
    async def empezar(self, ctx):
        p = self.leerjson()
        idmem = str(ctx.message.author.id)
        if idmem in p["jugadores"]:
            adver = await ctx.send(f'{ctx.message.author.mention} Tu personaje ya existe, si quieres resetearlo, de momento no puedes.')
            await asyncio.sleep(3)
            await adver.delete()
        else:
            p["jugadores"][idmem] = {}
            p["jugadores"][idmem]["slot"] = {}
            for i in range(27):
                p["jugadores"][idmem]["slot"][i] = ":blue_square:"
            p["jugadores"][idmem]["dinero"] = 0
            p["jugadores"][idmem]["nivel"] = 1
            p["jugadores"][idmem]["xp"] = 0
            p["jugadores"][idmem]["hp"] = 20
            p["jugadores"][idmem]["maxhp"] = 20
            p["jugadores"][idmem]["nxtnivel"] = 100
            p["jugadores"][idmem]["atq"] = 5
            p["jugadores"][idmem]["def"] = 2
            p["jugadores"][idmem]["vendiendo"] = None
            p["jugadores"][idmem]["luchando"] = None
            p["jugadores"][idmem]["nsitem"] = None
            p["jugadores"][idmem]["arma"] = None
            p["jugadores"][idmem]["armadura"] = None
            self.escribirjson(p)
            await ctx.send(f'{ctx.message.author.mention} Tu personaje ha sido iniciado con éxito.')

    #Comando que muestra el inventario del usuario
    @commands.command(aliases=['inv', 'objetos', 'obj'])
    async def inventario(self, ctx, columna = None, *, fila= None):
        p = self.leerjson()
        if str(ctx.message.author.id) in p["jugadores"]:
            if columna == None and fila == None:
                inv = self.visualizainv(p, str(ctx.message.author.id))
                inven = discord.Embed(
                    title="Inventario",
                    description=inv,
                    color = discord.Colour.blue()
                )
                await ctx.send(f'{ctx.message.author.mention}',embed=inven)
            else:
                try:
                    columna = int(columna)
                    fila = int(fila)
                except:
                    columna = "No"
                    fila = "No"
                if isinstance(columna, int) and isinstance(fila, int):
                    print("yet")
                else:
                    print("No")
        else:
            adver = await ctx.send(f'{ctx.message.author.mention} Aún no has creado un personaje, usa `rpg>empezar` para hacerlo.')
            await asyncio.sleep(3)
            await adver.delete()
    
    #Comando que muestra la estadística del usuario 
    @commands.command(aliases=['estadisticas', 'estadísticas', 'est', 'stat'])
    async def stats(self, ctx):
        p = self.leerjson()
        if str(ctx.message.author.id) in p["jugadores"]:
            idmem = str(ctx.message.author.id)
            vida = self.porvida(int(p["jugadores"][idmem]["hp"]), int(p["jugadores"][idmem]["maxhp"]))
            arma = ["Ninguna", ""]
            armadura = ["Ninguna", ""]
            if p["jugadores"][idmem]["arma"] != None:
                arma[0] = p["objetos"][p["jugadores"][idmem]["arma"]["name"]]["name"]
                arma[1] = p["objetos"][p["jugadores"][idmem]["arma"]["name"]]["emj_d"]
            if p["jugadores"][idmem]["armadura"] != None:
                armadura[0] = p["objetos"][p["jugadores"][idmem]["arma"]["name"]]["name"]
                armadura[1] = p["objetos"][p["jugadores"][idmem]["arma"]["name"]]["emj_d"]
            std = discord.Embed(
                title="Estadísticas",
                color = discord.Colour.blue()
            )
            std.set_thumbnail(
                url=ctx.message.author.avatar_url
            )
            std.add_field(
                name="Nivel",
                value=f':gear:{p["jugadores"][idmem]["nivel"]}',
                inline=False
            )
            std.add_field(
                name="HP",
                value=vida+f'\n{p["jugadores"][idmem]["hp"]}/{p["jugadores"][idmem]["maxhp"]}',
                inline=False
            )
            std.add_field(
                name="Ataque",
                value=f':crossed_swords:{p["jugadores"][idmem]["atq"]}',
                inline=False
            )
            std.add_field(
                name="Defensa",
                value=f':shield:{p["jugadores"][idmem]["def"]}',
                inline=False
            )
            std.add_field(
                name="Arma equipada",
                value=f'{arma[1]}{arma[0]}',
                inline=False
            )
            std.add_field(
                name="Armadura equipada",
                value=f'{armadura[1]}{armadura[0]}',
                inline=False
            )
            std.add_field(
                name="Siguente Nivel",
                value=f'{p["jugadores"][idmem]["xp"]}/{p["jugadores"][idmem]["nxtnivel"]}',
                inline=False
            )
            std.add_field(
                name="Dinero",
                value=f':moneybag:{p["jugadores"][idmem]["dinero"]}',
                inline=False
            )
            await ctx.send(f'{ctx.message.author.mention}', embed=std)
        else:
            adver = await ctx.send(f'{ctx.message.author.mention} Aún no has creado un personaje, usa `rpg>empezar` para hacerlo.')
            await asyncio.sleep(3)
            await adver.delete()
    
    @commands.command()
    async def explorar(self, ctx):
        p = self.leerjson()
        if str(ctx.message.author.id) in p["jugadores"]:
            idmem = str(ctx.message.author.id)
            if p["jugadores"][idmem]["luchando"] != None:
                adver = await ctx.send(f'{ctx.message.author.mention} Ya estás luchando contra algo.')
                await asyncio.sleep(3)
                await adver.delete()
            else:
                if p["jugadores"][idmem]["hp"] > 0:
                    for msj in p["mensajes"]:
                        if p["mensajes"][msj]["miembro"] == ctx.message.author.id:
                            del p["mensajes"][msj]
                    descareas = ""
                    reacts = []
                    rawareas = []
                    for area in p["areas"]:
                        if p["jugadores"][idmem]["nivel"] >= p["areas"][area]["minnivel"]:
                            if descareas == "":
                                descareas =f"{p['areas'][area]['react']}**"+p["areas"][area]["idname"]+"**"
                            else:
                                descareas = descareas+"\n"+f"{p['areas'][area]['react']}**"+p["areas"][area]["idname"]+"**"
                            reacts.append(p["areas"][area]["react"])
                            rawareas.append(p["areas"][area]["idname"])
                    areas = discord.Embed(
                        title="Lugares de exploración",
                        description=descareas+"\n*Elige un area*",
                        color = discord.Colour.blue()
                    )
                    mensaje = await ctx.send(f'{ctx.message.author.mention}', embed=areas)
                    for reacciones in reacts:
                        await mensaje.add_reaction(f"{reacciones}")
                    p["mensajes"][str(mensaje.id)] = {}
                    p["mensajes"][str(mensaje.id)]["reacts"] = reacts
                    p["mensajes"][str(mensaje.id)]["rawareas"] = rawareas
                    p["mensajes"][str(mensaje.id)]["miembro"] = idmem
                    p["mensajes"][str(mensaje.id)]["categoria"] = "e"
                    p["mensajes"][str(mensaje.id)]["procesando"] = False
                    self.escribirjson(p)
                else:
                    adver = await ctx.send(f'{ctx.message.author.mention} No tienes puntos de vida usa `rpg>descansar` para obtener más.')
                    await asyncio.sleep(3)
                    await adver.delete()
        else:
            adver = await ctx.send(f'{ctx.message.author.mention} Aún no has creado un personaje, usa `rpg>empezar` para hacerlo.')
            await asyncio.sleep(3)
            await adver.delete()
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        p = self.leerjson()
        idmem = str(reaction.user_id)
        if idmem != "730804779021762561":
            if str(reaction.message_id) in p["mensajes"]:
                emoji = None
                if reaction.emoji.id == None:
                    emoji = f"{reaction.emoji.name}"
                else: 
                    emoji = self.bot.get_emoji(reaction.emoji.id)
                if idmem != p["mensajes"][str(reaction.message_id)]["miembro"]:
                    await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                else:
                    z = False
                    indice = 0
                    for react in p["mensajes"][str(reaction.message_id)]["reacts"]:
                        if react == emoji:
                            z = True
                            break
                        indice += 1
                    if z:
                        if not p["mensajes"][str(reaction.message_id)]["procesando"]:
                            p["mensajes"][str(reaction.message_id)]["procesando"] = True
                            self.escribirjson(p)
                            if p["mensajes"][str(reaction.message_id)]["categoria"] == "e":
                                area = p["mensajes"][str(reaction.message_id)]["rawareas"][indice]
                                namon = randint(0, len(p["areas"][area.lower()])-4)
                                itemdrop = randint(1, 100)
                                monstruo = p["areas"][area.lower()][str(namon)]
                                dinerodrop = randint(monstruo["mindinero"], monstruo["maxdinero"])
                                nivel = randint(monstruo["minlevel"], monstruo["maxlevel"])
                                if itemdrop <= monstruo["objeto1"]["prob"]:
                                    itemdrop = monstruo["objeto1"]["name"]
                                elif itemdrop <= monstruo["objeto2"]["prob"]:
                                    itemdrop = monstruo["objeto2"]["name"]
                                else:
                                    itemdrop = monstruo["objeto3"]["name"]
                                luchando = {
                                    "id": namon,
                                    "area": area.lower(),
                                    "name": monstruo["name"],
                                    "nivel": nivel+1,
                                    "atq": monstruo["atqbase"] + int(nivel * 1.5),
                                    "hp": monstruo["hpbase"] + (nivel*2),
                                    "maxhp": monstruo["hpbase"] + (nivel*2),
                                    "def": monstruo["defbase"] + nivel,
                                    "prec": monstruo["prec"],
                                    "xp": monstruo["xpbase"] + nivel,
                                    "drop": itemdrop,
                                    "dinero": dinerodrop,
                                    "n": monstruo['n']
                                }
                                for react in p["mensajes"][str(reaction.message_id)]["reacts"]:
                                    await self.delreact(reaction.channel_id, 730804779021762561, reaction.message_id, react)
                                await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                                p["jugadores"][idmem]["luchando"] = luchando
                                p["mensajes"][str(reaction.message_id)] = {}
                                p["mensajes"][str(reaction.message_id)]["miembro"] = idmem
                                p["mensajes"][str(reaction.message_id)]["categoria"] = "l"
                                p["mensajes"][str(reaction.message_id)]["reacts"] = ["🔪", "💨"]
                                p["mensajes"][str(reaction.message_id)]["acciones"] = ["atacar", "escapar"]
                                p["mensajes"][str(reaction.message_id)]["procesando"] = False
                                mongrafichp = self.porvida(luchando["hp"], luchando["maxhp"])
                                playerhp = self.porvida(p["jugadores"][idmem]["hp"], p["jugadores"][idmem]["maxhp"])
                                lucha = discord.Embed(
                                    title=f"Luchando contra {monstruo['n']} **{monstruo['name']}**",
                                    description=f"Tu vida:{playerhp}{p['jugadores'][idmem]['hp']}/{p['jugadores'][idmem]['maxhp']}\n{monstruo['name']}:{mongrafichp}",
                                    color = discord.Colour.blue()
                                )
                                lucha.add_field(
                                    name="Narrador",
                                    value=f"Te has encotrado con {monstruo['n']} **{monstruo['name']}**",
                                    inline=False
                                )
                                canal = self.bot.get_channel(reaction.channel_id)
                                mensaj = await canal.fetch_message(reaction.message_id)
                                await mensaj.edit(embed=lucha)
                                for react in p["mensajes"][str(reaction.message_id)]["reacts"]:
                                    channel = self.bot.get_channel(reaction.channel_id)
                                    mensaje = await channel.fetch_message(reaction.message_id)
                                    await mensaje.add_reaction(react)
                                await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                            elif p["mensajes"][str(reaction.message_id)]["categoria"] == "l":
                                for react in p["mensajes"][str(reaction.message_id)]["reacts"]:
                                    await self.delreact(reaction.channel_id, 730804779021762561, reaction.message_id, react)
                                await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                                if p["mensajes"][str(reaction.message_id)]["acciones"][indice] == "atacar":
                                    player = p["jugadores"][idmem]
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
                                            p["jugadores"][idmem]["dinero"] += player['luchando']['dinero']
                                            p["jugadores"][idmem]["xp"] += player['luchando']['xp']
                                            noguardado = True
                                            for a in range(27):
                                                a1 = str(a)
                                                if player["slot"][a1] == ":blue_square:":
                                                    p["jugadores"][idmem]["slot"][a1] = {}
                                                    p["jugadores"][idmem]["slot"][a1]["item"] = player['luchando']['drop']
                                                    p["jugadores"][idmem]["slot"][a1]["cant"] = 1
                                                    noguardado = False
                                                    break
                                                elif "item" in player["slot"][a1]:
                                                    if player["slot"][a1]["item"] == player['luchando']['drop'] and player["slot"][a1]["cant"] < p["objetos"][player['luchando']['drop']]["max"]:
                                                        p["jugadores"][idmem]["slot"][a1]["cant"] += 1
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
                                            del p['mensajes'][str(reaction.message_id)]
                                            p["jugadores"][idmem]["luchando"] = None
                                            await mensaj.edit(embed=win)
                                        else:
                                            playerhp = self.porvida(player["hp"], player["maxhp"])
                                            mongrafichp = self.porvida(player["luchando"]["hp"], player["luchando"]["maxhp"])
                                            lucha = discord.Embed(
                                                title=f"Luchando contra {player['luchando']['n']} **{player['luchando']['name']}**",
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
                                            p["jugadores"][idmem]["luchando"]["hp"] = player["luchando"]["hp"]
                                            canal = self.bot.get_channel(reaction.channel_id)
                                            mensaj = await canal.fetch_message(reaction.message_id)
                                            await mensaj.edit(embed=lucha)
                                            await asyncio.sleep(2)
                                            enenm = self.acenemigo(p, idmem)
                                            p = enenm[0]
                                            await mensaj.edit(embed=enenm[1])
                                            if enenm[2]:
                                                del p["mensajes"][str(reaction.message_id)]
                                            else:
                                                p["mensajes"][str(reaction.message_id)]["procesando"] = False
                                                for react in p["mensajes"][str(reaction.message_id)]["reacts"]:
                                                    channel = self.bot.get_channel(reaction.channel_id)
                                                    mensaje = await channel.fetch_message(reaction.message_id)
                                                    await mensaje.add_reaction(react)
                                    else:
                                        mongrafichp = self.porvida(player["luchando"]["hp"], player["luchando"]["maxhp"])
                                        playerhp = self.porvida(player["hp"], player["maxhp"])
                                        lucha = discord.Embed(
                                            title=f"Luchando contra {player['luchando']['n']} **{player['luchando']['name']}**",
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
                                        enenm = self.acenemigo(p, idmem)
                                        p = enenm[0]
                                        await mensaj.edit(embed=enenm[1])
                                        if enenm[2]:
                                            del p["mensajes"][str(reaction.message_id)]
                                        else:
                                            p["mensajes"][str(reaction.message_id)]["procesando"] = False
                                            for react in p["mensajes"][str(reaction.message_id)]["reacts"]:
                                                channel = self.bot.get_channel(reaction.channel_id)
                                                mensaje = await channel.fetch_message(reaction.message_id)
                                                await mensaje.add_reaction(react)
                                elif p["mensajes"][str(reaction.message_id)]["acciones"][indice] == "escapar":
                                    intento = randint(1, 100)
                                    if intento > 50:
                                        for react in p["mensajes"][str(reaction.message_id)]["reacts"]:
                                            await self.delreact(reaction.channel_id, 730804779021762561, reaction.message_id, react)
                                        del p["mensajes"][str(reaction.message_id)]
                                        escape = discord.Embed(
                                            title="Escape",
                                            color = discord.Colour.blue()
                                        )
                                        escape.add_field(
                                            name="Narrador",
                                            value="Escapaste con éxito del combate",
                                            inline=False
                                        )
                                        p["jugadores"][idmem]["luchando"] = None
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
                                        enenm = self.acenemigo(p, idmem)
                                        p = enenm[0]
                                        await mensaj.edit(embed=enenm[1])
                                        if enenm[2]:
                                            del p["mensajes"][str(reaction.message_id)]
                                        else:
                                            p["mensajes"][str(reaction.message_id)]["procesando"] = False
                                            for react in p["mensajes"][str(reaction.message_id)]["reacts"]:
                                                channel = self.bot.get_channel(reaction.channel_id)
                                                mensaje = await channel.fetch_message(reaction.message_id)
                                                await mensaje.add_reaction(react)
                            self.escribirjson(p)
                        else:
                            await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)
                    else:
                        await self.delreact(reaction.channel_id, reaction.user_id, reaction.message_id, emoji)

    @commands.command()
    async def descansar(self, ctx):
        p = self.leerjson()
        if str(ctx.message.author.id) in p["jugadores"]:
            if p["jugadores"][str(ctx.message.author.id)]["luchando"] == None:
                idmem = str(ctx.message.author.id)
                p["jugadores"][idmem]["dinero"] -= 3
                if p["jugadores"][idmem]["dinero"] < 0:
                    p["jugadores"][idmem]["dinero"] = 0
                p["jugadores"][idmem]["hp"] = p["jugadores"][idmem]["maxhp"]
                self.escribirjson(p)
                bien = await ctx.send(f'{ctx.message.author.mention}, Tu vída ha sido recuperada con éxito')
                await asyncio.sleep(3)
                await bien.delete()
            else:
                adver = await ctx.send(f'{ctx.message.author.mention} No puedes hacer eso mientras estás en medio de una lucha.')
                await asyncio.sleep(3)
                await adver.delete()
        else:
            adver = await ctx.send(f'{ctx.message.author.mention} Aún no has creado un personaje, usa `rpg>empezar` para hacerlo.')
            await asyncio.sleep(3)
            await adver.delete()

def setup(bot):
    bot.add_cog(GameCommands(bot))