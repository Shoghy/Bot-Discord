import discord
from xlrd import open_workbook as open_excel

excel = open_excel("cogs\\idiomas.xlsx")
bot_i = excel.sheet_by_name("bot")

def embed_moderador(moderador, persona, razon, server, muted_warn, idioma):
    """Esta función crea un embed para que los moderadores y admins del sever
    lleven un historial de quienes han sido muteados/expulsados/baneados y por qué"""

    mod_embed = discord.Embed(title=f"{bot_i.cell_value(44, idioma)}", color = discord.Colour.red())
    mod_embed.set_author(
        name=f"[{bot_i.cell_value(muted_warn, idioma)}] {persona.display_name}",
        icon_url=str(persona.avatar_url))
    mod_embed.add_field(name=f"{bot_i.cell_value(49, idioma)}", value=f"{persona.mention}", inline=True)
    mod_embed.add_field(name=f"{bot_i.cell_value(muted_warn+1, idioma)}", value=f"{moderador}", inline=True)
    mod_embed.add_field(name=f"{bot_i.cell_value(50, idioma)}", value=razon, inline=True)
    return mod_embed