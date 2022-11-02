import discord
from discord.ext import commands
from __main__ import bot, prefijo, dni
from cogs.moderacion import ModeracionCommands as mod

bot2 = bot if isinstance(bot, commands.Bot) else None
discord.Button()
@bot.slash_command(
    guilds_id=[730084778061332550],
    name=f"{prefijo}dni",
    description="Muestra el dni de una persona."
)
@discord.option(
    "person",
    discord.Member,
    description="La persona a la que le quieres ver el dni, por defecto tú mismo.",
    required=False,
    default=None,
    guild_only=True
)
async def dni1(ctx : discord.ApplicationContext, person):
    await ctx.defer()
    file = await dni(ctx, person)
    a = await ctx.respond(file=file)
    file.close()

#=======================================================================================================

@bot.slash_command(
    guilds_id=[730084778061332550],
    name=f"{prefijo}tempmute",
    description="Silencia de manera temporal a una persona."
)
@discord.option(
    "miembro",
    discord.Member,
    description="El miembro al cual se quiere silenciar.",
    required=True,
    guild_only=True
)
@discord.option(
    "tiempo",
    int,
    description="El tiempo (en segundos) que el miembro va a esperar para ser desmuteado.",
    required=True,
    guild_only=True
)
@discord.option(
    "razon",
    str,
    description="El por qué se está silenciando a ese miembro.",
    required=False,
    default="Sin especificar",
    guild_only=True
)
async def tempmute(ctx : commands.Context, member : discord.Member, tiempo : int, *, razon : str = "Sin especificar"):
    await ctx.defer()
    await mod.tempmute(ctx, member, tiempo, razon)