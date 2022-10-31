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
import asyncio
from random import randint

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
    if len(name) > 28:
        name = name[:28]+"\n"+name[28:]
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
    try:
        esclavo = discord.utils.get(member.guild.roles, id=726901624215306332)
        await member.add_roles(role)
    except :
        await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Ocurrió un error al intentar añadir el role Esclavos')
    switcher = {
        1: f'{member.mention} Bienvenid@ a **La Hermandad**',
        2: f'{member.mention} se ha unido a la partida\n**<La Hermandad>** Bienvenido',
        3: f'¡Acabó de llegar {member.mention} a **La Hermandad**! ¡Denle la bienvenida!'
    }
    mensaje = switcher.get(randint(1, 3))
    await channel.send(f'{mensaje}', file=file)
    remove(str(member.id)+".png")

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(737135104450756631)
    despedida = await channel.send(f'{member.mention} Adiós, te extrañaremos.')
    await despedida.add_reaction('👋')

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
    if cant != None and isinstance(cant, int) and cant >= 0:
        for role in ctx.message.author.roles:
            if str(role) in roles_admin and msgdeleted:
                msgdeleted = False
                async for message in ctx.channel.history(limit=cant+1):
                    await message.delete()
        if msgdeleted:
            await ctx.send(f'{ctx.message.author.mention} No puedes usar ese comando, no eres admin.')
        else:
            if cant != 1:
                listo = await ctx.send(f'He borrado `{cant} mensajes`.')
                await asyncio.sleep(3)
                await listo.delete()
            else:
                listo = await ctx.send(f'He borrado `{cant} mensaje`.')
                await asyncio.sleep(3)
                await listo.delete()
    else:
        if cant < 0:
            er = await ctx.send(f'{ctx.message.author.mention} La cantidad de mensajes debe ser mayor a 0.')
            await asyncio.sleep(5)
            await er.delete()
        else:
            er = await ctx.send(f'{ctx.message.author.mention} Debes poner la cantidad de mensajes que quieras borrar `rpg>clear <num>`.')
            await asyncio.sleep(5)
            await er.delete()

@bot.event
async def on_message(msg):
    await bot.process_commands(msg)
    if msg.channel.id == 726903015579058206:
        if msg.attachments:
            if len(msg.attachments) == 1:
                pic_ext = ['.jpg','.png','.jpeg', '.gif', '.mp4', '.mp3', '.webp']
                arcnombre = msg.attachments[0].filename.lower()
                for ext in pic_ext:
                    if arcnombre.endswith(ext):
                        await msg.add_reaction('👍')
                        await msg.add_reaction('👎')
            else:
                await msg.delete()
                pls = await msg.channel.send(f'{msg.author.mention}, envia una imagen/video a la vez.')
                await asyncio.sleep(3)
                await pls.delete()

#Mensaje de error
@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, commands.CommandNotFound):
        await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Ocurrió un error:\n{error}')
    else:
        msgerror = await ctx.send(f'{ctx.message.author.mention} Comando inexistente.')
        await asyncio.sleep(3)
        await msgerror.delete()

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
        await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Límite de consultas exdidas :\'v.')
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
        await asyncio.sleep(5)
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
            await video_spam.add_reaction('👍')
        #&maxResults=1
        ant[1] = nuev[1]
    elif nuev[1] < ant[1]:
        ant[1] = nuev[1]

for filename in listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

#Token del bot
bot.run(getenv("DISCORD_SECRET_KEY"))
#bot.run(getenv("prueba_bot"))