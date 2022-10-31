#Imports
import discord
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from requests import get
from io import BytesIO
from os import remove, listdir, getenv
from dotenv import load_dotenv
from pathlib import Path
import json
import sys
from time import sleep

#Obtener los datos del archivo .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#Variables universales
api_key = getenv("api_key")
channel_id = "UCXhBotdryMg1N5Mju4dkIcA"
ant = [1, 2]
roles_admin = ["Canciller", "Rey", "Sacerdote", "Duque"]
url = [1, 2]
url[0] = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}'
url[1] = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=id&order=date'
sys.dont_write_bytecode = True

#Prefix del bot
bot = commands.Bot(command_prefix='rpg>')
#bot = commands.Bot(command_prefix='prb>')

#Función que crea el dni
def imgdni(avatar, nac, name : str, id : int):
    dni = Image.open("DNI.png")
    url_img = get(avatar)
    avatarimg = Image.open(BytesIO(url_img.content))
    avlittle = avatarimg.resize((250, 250))
    mask_im = Image.new("L", avlittle.size, 0)
    draw = ImageDraw.Draw(mask_im)
    draw.ellipse((10, 10, 240, 240), fill=255)
    mask_im_blur = mask_im.filter(ImageFilter.GaussianBlur(2))
    font = ImageFont.truetype("calibril.ttf", 24)
    font2 = ImageFont.truetype("calibril.ttf", 57)
    dni.paste(avlittle, (0, 0), mask_im_blur)
    draw = ImageDraw.Draw(dni)
    draw.text((405, 83), name,(255,255,255),font=font)
    draw.text((446, 249), nac.strftime("%d")+"-"+nac.strftime("%m")+"-"+nac.strftime("%Y"),(255,255,255),font=font)
    draw.text((7, 443), str(id),(255,255,255),font=font2)
    dni.save(str(id)+".png")

#Mensaje que se escribe cuando el bot ya está funcionando
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('rpg>help'))
    json_url = get(url[0])
    data = json.loads(json_url.text)
    try:
        ant[0] = int(data["items"][0]["statistics"]["subscriberCount"]) - 1
        ant[1] = int(data["items"][0]["statistics"]["videoCount"])
        subcount.start()
    except:
        print("El contador de subs y videos nuevos no se podrá")
    print("Estoy listo")

#Mensaje que se muestra cuando alguien nuevo entra al server
@bot.event
async def on_member_join(member):
    imgdni(member.avatar_url, member.joined_at, member.display_name, member.id)
    file = discord.File(str(member.id)+".png")
    channel = bot.get_channel(726877963345330289)
    await channel.send(f'{member.mention} Bienvenid@ a la hermandad', file=file)
    remove(str(member.id)+".png")

#Comando que enseña el dni de un integrante
@bot.command(aliases=['cedula', 'documento', 'doc', 'cédula'])
async def dni(ctx, *, person : discord.Member = None):
    if person == None:
        imgdni(ctx.message.author.avatar_url, ctx.message.author.joined_at, ctx.message.author.name, ctx.message.author.id)
        file = discord.File(str(ctx.message.author.id)+".png")
        await ctx.send(file=file)
        try:
            remove(str(ctx.message.author.id)+".png")
        except:
            pass
    else:
        imgdni(person.avatar_url, person.joined_at, person.display_name, person.id)
        file = discord.File(str(person.id)+".png")
        await ctx.send(file=file)
        try:
            remove(str(person.id)+".png")
        except:
            pass

#Comando para borrar mensajes
@bot.command(aliases=['borrar', 'purgar', 'msgkill', 'delete'])
async def clear(ctx, *, cant = None):
    msgdeleted = True
    try:
        cant = int(cant)
    except:
        cant = str("no")
    if cant != None and isinstance(cant, int):
        for role in ctx.message.author.roles:
            if str(role) in roles_admin and msgdeleted:
                msgdeleted = False
                async for message in ctx.channel.history(limit=cant+1):
                    await message.delete()
        if msgdeleted:
            await ctx.send(f'{ctx.message.author.mention} No puedes usar ese comando, no eres admin.')
        else:
            listo = await ctx.send(f'He borrado `{cant} mensajes`.')
            sleep(3)
            await listo.delete()
    else:
        await ctx.send(f'{ctx.message.author.mention} Debes poner la cantidad de mensajes que quieras borrar `rpg>clear <num>`.')

#Mensaje de error
@bot.event
async def on_command_error(ctx, error):
    print(error)

#Loop que muestra cuando alguien se suscribe y los vídeos nuevos
@tasks.loop(seconds=25)
async def subcount():
    message = await bot.get_channel(735917504521830431).fetch_message(735938304356384859)
    video_channel = bot.get_channel(726910405116690494)
    nuev = [1, 2]
    json_url = get(url[0])
    data = json.loads(json_url.text)
    try:
        nuev[0] = int(data["items"][0]["statistics"]["subscriberCount"])
        nuev[1] = int(data["items"][0]["statistics"]["videoCount"])
    except:
        await bot.get_channel(736207259327266881).send("Límite de consultas exdidas :'v.")
        subcount.cancel()
    if ant[0] != nuev[0]:
        contenido = ""
        n = str(nuev[0])
        for a in range(len(n)):
            switcher = {
                0: ":zero:",
                1: ":one:",
                2: ":two:",
                3: ":three:",
                4: ":four:",
                5: ":five:",
                6: ":six:",
                7: ":seven:",
                8: ":eight:",
                9: ":nine:"
            }
            contenido = contenido + switcher.get(int(n[a]))
        await message.edit(content=contenido)
        meta = pow(10, len(n)-1)
        if meta <= nuev[0] and ant[0] < meta:
            await bot.get_channel(726910120839086261).send(f'@everyone Hemos llegado a los {meta} subscriptores, muchas gracias.')
        ant[0] = nuev[0]
    if nuev[1] > ant[1]:
        cvideos = nuev[1] - ant[1]
        url[1] = url[1] + f'&maxResults={cvideos}'
        sleep(5)
        json_url = get(url[1])
        data = json.loads(json_url.text)
        idvideo = ""
        for a in range(cvideos):
            try:
                idvideo = data["items"][a]["id"]["videoId"]
            except:
                await bot.get_channel(736207259327266881).send("Límite de consultas exdidas :'v.")
                subcount.cancel()
            video_spam = await video_channel.send(f'@everyone ¡Violet Ink Band ha subido un nuevo vídeo! Ve a verlo https://www.youtube.com/watch?v={str(idvideo)}')
            daco = bot.get_emoji(726945073593319445)
            await video_spam.add_reaction(daco)
        #&maxResults=1
        ant[1] = nuev[1]
    elif nuev[1] < ant[1]:
        ant[1] = nuev[1]

for filename in listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
#Token del bot
bot.run(getenv("DISCORD_SECRET_KEY"))