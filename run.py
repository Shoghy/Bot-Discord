from hermandiano import bot
from os import getenv

#Mensaje de error
"""@bot.event
async def on_command_error(ctx, error):
    print(error)"""

#Ejecuta el bot
#bot.run(getenv("DISCORD_SECRET_KEY"))
bot.run(getenv("prueba_bot"))