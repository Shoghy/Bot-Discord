import discord
from discord.ext import commands
import json

class GameCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def leerjson(self):
        jugador = None
        with open("cogs/personajes.json", 'r') as contenido:
            jugador = json.load(contenido)
        return jugador
    
    def escribirjson(self, jugador):
        with open("cogs/personajes.json", 'w') as contenido:
            json.dump(jugador, contenido)

    def visualizainv(self, jugador, idmem):
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

    @commands.command(aliases=['comenzar', 'start', 'inicio'])
    async def empezar(self, ctx):
        p = self.leerjson()
        if str(ctx.message.author.id) in p:
            await ctx.send(f'{ctx.message.author.mention} Tu personaje ya existe, si quieres resetearlo, de momento no puedes.')
        else:
            idmem = ctx.message.author.id
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
            self.escribirjson(p)
            await ctx.send(f'{ctx.message.author.mention} Tu personaje ha sido iniciado con éxito.')

    @commands.command(aliases=['inv', 'objetos', 'obj'])
    async def inventario(self, ctx):
        p = self.leerjson()
        if str(ctx.message.author.id) in p:
            inv = self.visualizainv(p, str(ctx.message.author.id))
            inven = discord.Embed(
                title="Inventario",
                color = discord.Colour.blue()
            )
            inven.add_field(name=ctx.message.author, value=inv)
            await ctx.send(embed=inven)
        else:
            await ctx.send(f'{ctx.message.author.mention} Aún no has creado un personaje, usa `prb>empezar` para hacerlo.')

def setup(bot):
    bot.add_cog(GameCommands(bot))