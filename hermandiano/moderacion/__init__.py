import discord
from discord.ext import commands
from typing import Union
from hermandiano import bot_i, exl, bot
from asyncio import sleep, run
from time import sleep as sleep2

fecha_formato = "%d/%m/%Y %H:%M"

def permiso(member : discord.Member, server_config):
    """Esta función revisa si el usuario puede usar el comando que trató de ejecutar"""

    permiso = False
    if member.guild_permissions.administrator:
        permiso = True

    elif "role_mod" in server_config:
        if member.get_role(int(server_config["role_mod"])) != None:
            permiso = True

    return permiso

async def revision(member : discord.Member, ctx : commands.Context, server_config, idioma):
    """Esta función revisa si el usuario puede usar los comandos de moderación en x persona
    y le avisa en caso de que no"""

    permiso = True
    if member.guild_permissions.administrator:
        permiso = False
        await advertir(idioma, 41, ctx)

    elif "role_mod" in server_config:
        if member.get_role(server_config["role_mod"]) != None:
            if not ctx.author.guild_permissions.administrator:
                permiso = False
                await advertir(idioma, 42, ctx)
    return permiso

async def advertir(idioma : int, oracion : int, ctx : Union[commands.Context, discord.ApplicationContext]):
    """Esto despliega un mensaje si el miembro intenta usar una función
    a la cual no tiene acceso"""

    adver = None
    mensaje = f'{bot_i.cell_value(oracion, idioma)}'
    if isinstance(ctx, commands.Context):
        adver = await ctx.reply(mensaje)
    elif isinstance(ctx, discord.ApplicationContext):
        adver = await ctx.respond(mensaje)

    try:
        adver.delete(delay=3)
    except:
        pass

def segundo_hilo(is_async : bool, funcion, tiempo : float = None, parametros : dict = None):
    """Esta función se usa para que otras funciones se ejecuten en segundo plano"""

    async def do_something_sc(funcion2, tiempo = None, parametros = None):
        if tiempo != None:
            await sleep(tiempo)

        if parametros == None:
            await funcion2()
        else:
            await funcion2(**parametros)

    if is_async:
        run(do_something_sc(funcion, tiempo, parametros))
    else:
        if tiempo != None:
            sleep2(tiempo)

        if parametros == None:
            funcion()
        else:
            funcion(**parametros)

def mod_embed(moderador : discord.Member, member_mention : str, consecuencia : int, idioma, titulo : int, razon : str):
    """Esta función crea un embed para que los moderadores y admins del sever
    lleven un historial de quienes han sido muteados/expulsados/baneados y por qué"""
    color = 0
    if titulo == 46:
        color = discord.Colour.red()
    else:
        color = 0xebe40f

    #titulo 45 advertencia
    #titulo 46 castigo
    mod_embed = discord.Embed(
        title=f"{bot_i.cell_value(titulo, idioma)}",
        color=color
    )

    mod_embed.set_author(
        name=f"{moderador.display_name}",
        icon_url=str(moderador.avatar_url)
    )
    castigo_i = exl.sheet_by_name("castigos")

    descripcion = str(bot_i.cell_value(44, idioma))
    descripcion = descripcion.replace("{member}", member_mention)
    
    #Consecuencia 1: avisado
    #Consecuencia 2: silenciado
    #Consecuencia 3: baneado temporalmente
    #Consecuencia 4: expulsado
    #Consecuencia 5: baneado

    descripcion = descripcion.replace("{consecuencia}", castigo_i.cell_value(consecuencia, idioma))
    descripcion = descripcion.replace("{mod}", moderador.mention)

    mod_embed.add_field(
        name=f"{bot_i.cell_value(53, idioma)}",
        value=descripcion,
        inline=False
    )
    mod_embed.add_field(
        name=f"{bot_i.cell_value(49, idioma)}",
        value=razon,
        inline=False
    )
    return mod_embed

async def silenciar_tban(member : discord.Member, tiempo, sil_tban : bool, role = None):
    """Esta función administra silencios temporales y baneos temporales.
    Se encarga de aplicarlos y de quitarlos"""

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

async def canal_moderador(server_conf, msg = None, embed = None, file = None):
    if "canal_moderacion" in server_conf:
        canal_moderacion = server_conf["canal_moderacion"]
        try:
            canal = bot.get_channel(int(canal_moderacion))
            await canal.send(content=msg, embed=embed, file=file)
        except discord.NotFound:
            pass

from . import tempmute
from . import warn