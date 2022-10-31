import discord
from xlrd import open_workbook as open_excel

excel = open_excel("cogs\\idiomas.xlsx")
bot_i = excel.sheet_by_name("bot")

def mod_embed(moderador : discord.Member, member : discord.Member, castigo : int, idioma, titulo, razon : str):
    """Esta función crea un embed para que los moderadores y admins del sever
    lleven un historial de quienes han sido muteados/expulsados/baneados y por qué"""
    color = None
    if titulo == 46:
        color = discord.Colour.red()
    else:
        color = 0xebe40f

    mod_embed = discord.Embed(
        title=f"{bot_i.cell_value(titulo, idioma)}",
        color =color
    )
    mod_embed.set_author(
        name=f"{moderador.display_name}",
        icon_url=str(moderador.avatar_url)
    )
    castigo_i = excel.sheet_by_name("castigos")

    informacion = str(bot_i.cell_value(44, idioma))
    informacion = informacion.replace("{member}", member.mention)
    informacion = informacion.replace("{castigo}", castigo_i.cell_value(castigo, idioma))
    informacion = informacion.replace("{mod}", moderador.mention)

    mod_embed.add_field(
        name=f"{bot_i.cell_value(53, idioma)}",
        value=informacion,
        inline=False
    )
    mod_embed.add_field(
        name=f"{bot_i.cell_value(49, idioma)}",
        value=razon,
        inline=False
    )
    return mod_embed