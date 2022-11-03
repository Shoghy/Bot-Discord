from hermandiano import bot, imgdni, Datos, bot_i
from typing import Union
from discord.ext import commands
import discord
from asyncio import sleep

#Comando que enseña el dni de un integrante y manda una alerta si el miembro no tiene permiso para usar ese comando
#@bot.slash_command(guilds_id=[730084778061332550])
@bot.command(aliases=['cedula', 'documento', 'cédula'])
async def dni(ctx : Union[commands.Context, discord.ApplicationContext], person : discord.Member = None):
    server_id = str(ctx.guild.id)
    server_conf = Datos.get("servers/"+server_id+"/configs")
    canales_comandos = Datos.get("servers/"+server_id+"/canales_comandos")
    idioma = server_conf["idioma"]

    #Esta parte determina si el usuario puede o no usar este comando en el canal que fue ejecutado
    permisoconcedido = False
    if ctx.author.guild_permissions.administrator:
        permisoconcedido = True
    else:
        if canales_comandos != False:
            canal_id = str(ctx.channel.id)
            if canal_id in canales_comandos:
                permisoconcedido = True
            elif canales_comandos == True:
                permisoconcedido = True

    if permisoconcedido:
        nacionalidad = "Sin nacionalidad"
        if "nacionalidad" in server_conf:
            nacionalidad = server_conf["nacionalidad"]

        if person == None:
            person = ctx.author
        avatar = person.avatar
        fecha_ingreso = person.joined_at
        grupo_logo = ctx.guild.icon
        nombre = person.display_name
        identificador = person.id
        file = await imgdni(avatar, fecha_ingreso, grupo_logo, nombre, identificador, nacionalidad)
        if isinstance(ctx, commands.Context):
            await ctx.reply(file=file)
            file.close()
        else:
            return file
    else:
        aviso = None
        if canales_comandos == False:
            msg = bot_i.cell_value(55, idioma)
            aviso = await ctx.message.reply(f"{msg}")

        else:
            msg = bot_i.cell_value(1, idioma)
            canales = ""

            for canal in canales_comandos:
                canales += f" <#{canal}>"

            msg = msg.replace("{canales}", canales)
            aviso = await ctx.reply(f"{msg}")

        await sleep(5)
        try:
            await aviso.delete()
        except discord.NotFound:
            pass