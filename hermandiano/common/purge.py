from hermandiano import bot, Datos, bot_i
from typing import Union
from discord.ext import commands
import discord
from asyncio import sleep

#Comando para borrar mensajes
@bot.command(aliases=['borrar', 'msgkill', 'delete', 'purge'])
async def clear(ctx : Union[commands.Context, discord.ApplicationContext], cant : int = 0):
    server_id = str(ctx.message.guild.id)
    server_conf = Datos.get("servers/"+server_id+"/configs")
    idioma = server_conf["idioma"]

    #Sólo los administradores pueden ejecutar este mensaje
    if ctx.author.guild_permissions.administrator:
        if cant > 0 and cant <= 300:
            borrados = 0
            if not ctx.message.mentions:
                borrados = await ctx.channel.purge(limit=cant)
            else:
                borrados = await ctx.channel.purge(limit=cant, check=ctx.message.mentions[0])

            msg = bot_i.cell_value(3, idioma)
            msg = msg.replace("{cant}", f"{len(borrados)}")
            listo = await ctx.send(msg)
            await sleep(3)
            try:
                await listo.delete()
            except discord.NotFound:
                pass

        else:
            msg = bot_i.cell_value(4, idioma)
            er = await ctx.send(f'{ctx.author.mention} {msg}')
            await sleep(3)
            try:
                await er.delete()
            except discord.NotFound:
                pass
    else:
        msg = bot_i.cell_value(5, idioma)
        adver = await ctx.send(f'{ctx.author.mention} {msg}')
        await sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass