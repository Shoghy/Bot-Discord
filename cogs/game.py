import discord
from discord.ext import commands
import json
from random import randint

class GameCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Devuelve los valores del archivo json
    def leerjson(self):
        jugador = None
        with open("cogs/personajes.json", 'r') as contenido:
            jugador = json.load(contenido)
        return jugador

    #Añade los cambios al archivo json
    def escribirjson(self, jugador):
        with open("cogs/personajes.json", 'w') as contenido:
            json.dump(jugador, contenido)

    #Devuelve un strings con los huecos del inventario
    def visualizainv(self, jugador, idmem : str):
        casillas = ":x::one: :two: :three: :four: :five: :six: :seven: :eight: :nine:\n:one:"
        for i in range(27):
            if "name" in jugador[idmem]["slot"][str(i)]:
                casillas = casillas + jugador["objetos"][jugador[idmem]["slot"][str(i)]["name"]]
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

    #Comando que inicializa al usuario
    @commands.command(aliases=['comenzar', 'start', 'iniciar'])
    async def empezar(self, ctx):
        p = self.leerjson()
        if str(ctx.message.author.id) in p:
            await ctx.send(f'{ctx.message.author.mention} Tu personaje ya existe, si quieres resetearlo, de momento no puedes.')
        else:
            idmem = str(ctx.message.author.id)
            p[idmem] = {}
            p[idmem]["slot"] = {}
            for i in range(27):
                p[idmem]["slot"][i] = ":blue_square:"
            p[idmem]["dinero"] = 0
            p[idmem]["nivel"] = 1
            p[idmem]["xp"] = 0
            p[idmem]["hp"] = 20
            p[idmem]["maxhp"] = 20
            p[idmem]["nxtnivel"] = 100
            p[idmem]["atq"] = 5
            p[idmem]["def"] = 2
            p[idmem]["vendiendo"] = None
            p[idmem]["luchando"] = None
            p[idmem]["nsitem"] = None
            p[idmem]["arma"] = None
            p[idmem]["armadura"] = None
            self.escribirjson(p)
            await ctx.send(f'{ctx.message.author.mention} Tu personaje ha sido iniciado con éxito.')

    #Comando que muestra el inventario del usuario
    @commands.command(aliases=['inv', 'objetos', 'obj'])
    async def inventario(self, ctx, columna = None, *, fila= None):
        p = self.leerjson()
        if str(ctx.message.author.id) in p:
            if columna == None and fila == None:
                inv = self.visualizainv(p, str(ctx.message.author.id))
                inven = discord.Embed(
                    title="Inventario",
                    color = discord.Colour.blue()
                )
                inven.add_field(name=ctx.message.author, value=inv)
                await ctx.send(embed=inven)
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
            await ctx.send(f'{ctx.message.author.mention} Aún no has creado un personaje, usa `prb>empezar` para hacerlo.')
    
    #Comando que muestra la estadística del usuario 
    @commands.command(aliases=['estadisticas', 'estadísticas', 'est', 'stat'])
    async def stats(self, ctx):
        p = self.leerjson()
        if str(ctx.message.author.id) in p:
            idmem = str(ctx.message.author.id)
            vida = self.porvida(int(p[idmem]["hp"]), int(p[idmem]["maxhp"]))
            arma = ["Ninguna", ""]
            armadura = ["Ninguna", ""]
            if p[idmem]["arma"] != None:
                arma[0] = p["objetos"][p[idmem]["arma"]["name"]]["name"]
                arma[1] = p["objetos"][p[idmem]["arma"]["name"]]["emj_d"]
            if p[idmem]["armadura"] != None:
                armadura[0] = p["objetos"][p[idmem]["arma"]["name"]]["name"]
                armadura[1] = p["objetos"][p[idmem]["arma"]["name"]]["emj_d"]
            std = discord.Embed(
                title="Estadísticas",
                color = discord.Colour.blue()
            )
            std.set_thumbnail(
                url=ctx.message.author.avatar_url
            )
            std.add_field(
                name="Nivel",
                value=f':gear:{p[idmem]["nivel"]}',
                inline=False
            )
            std.add_field(
                name="HP",
                value=vida+f'\n{p[idmem]["hp"]}/{p[idmem]["maxhp"]}',
                inline=False
            )
            std.add_field(
                name="Ataque",
                value=f':crossed_swords:{p[idmem]["atq"]}',
                inline=False
            )
            std.add_field(
                name="Defensa",
                value=f':shield:{p[idmem]["def"]}',
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
                value=f'{p[idmem]["xp"]}/{p[idmem]["nxtnivel"]}',
                inline=False
            )
            std.add_field(
                name="Dinero",
                value=f':moneybag:{p[idmem]["dinero"]}',
                inline=False
            )
            await ctx.send(f'{ctx.message.author.mention}', embed=std)
        else:
            await ctx.send(f'{ctx.message.author.mention} Aún no has creado un personaje, usa `prb>empezar` para hacerlo.')
    
    """@commands.command()
    async def explorar(self, ctx, *, lugar : str = "ramdon"):
        print("")"""

def setup(bot):
    bot.add_cog(GameCommands(bot))