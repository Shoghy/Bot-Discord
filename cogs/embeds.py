import discord
from xlrd import open_workbook as open_excel

excel = open_excel("cogs\\idiomas.xlsx")
bot_i = excel.sheet_by_name("bot")

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
    castigo_i = excel.sheet_by_name("castigos")

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