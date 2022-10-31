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
from datetime import date, datetime
from time import sleep

#Obtener los datos del archivo .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#Variables universales
api_key = getenv("api_key")
violet_idchannel = "UCXhBotdryMg1N5Mju4dkIcA"
dummer_idcahnnel = "UCwE_1B20UxznlQLtE0jU6pQ"
ant = [1, 2, 3, 4]
roles_admin = ["Canciller", "Rey", "Sacerdote", "Duque"]
url = [1, 2]
url[0] = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={violet_idchannel}&key={api_key}'
url[1] = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={dummer_idcahnnel}&key={api_key}'
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
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('0.0.5'))
    json_url = get(url[0])
    data = json.loads(json_url.text)
    json_url = get(url[1])
    data2 = json.loads(json_url.text)
    try:
        ant[0] = int(data["items"][0]["statistics"]["subscriberCount"]) - 1
        ant[1] = int(data["items"][0]["statistics"]["videoCount"])
        ant[2] = int(data2["items"][0]["statistics"]["subscriberCount"]) - 1
        ant[3] = int(data2["items"][0]["statistics"]["videoCount"])
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
        await member.add_roles(esclavo)
    except :
        await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Ocurrió un error al intentar añadir el role Esclavos')
    switcher = {
        1: f'{member.mention} Bienvenid@ a **La Hermandad**',
        2: f'{member.mention} se ha unido a la partida\n<**La Hermandad**> Bienvenido',
        3: f'¡Acabó de llegar {member.mention} a **La Hermandad**! ¡Denle la bienvenida!'
    }
    mensaje = switcher.get(randint(1, 3))
    await channel.send(f'{mensaje}', file=file)
    remove(str(member.id)+".png")

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(737135104450756631)
    despedida = await channel.send(f'**{member.display_name}** Adiós, te extrañaremos.')
    await despedida.add_reaction('👋')

#Comando que enseña el dni de un integrante
@bot.command(aliases=['cedula', 'documento', 'doc', 'cédula'])
async def dni(ctx, *, person : discord.Member = None):
    hecho = True
    if ctx.channel.id == 726905119894929531:
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
    else:    
        for role in ctx.message.author.roles:
            if str(role) in roles_admin and hecho:
                hecho = False
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
        if hecho:
            await ctx.message.delete()
            no = await ctx.send(f'{ctx.message.author.mention}, No puedes usar el comando en este canal')
            await asyncio.sleep(3)
            await no.delete()

#Comando para borrar mensajes
@bot.command(aliases=['borrar', 'purgar', 'msgkill', 'delete'])
async def clear(ctx, *, cant = None):
    msgdeleted = True
    try:
        cant = int(cant)
        if cant <= 0:
            cant = str("no")
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
            if cant != 1:
                listo = await ctx.send(f'He borrado `{cant} mensajes`.')
                await asyncio.sleep(3)
                await listo.delete()
            else:
                listo = await ctx.send(f'He borrado `{cant} mensaje`.')
                await asyncio.sleep(3)
                await listo.delete()
    else:
        er = await ctx.send(f'{ctx.message.author.mention} Debes poner la cantidad de mensajes que quieras borrar `rpg>clear <num>` y el número debe ser mayor a 0.')
        await asyncio.sleep(3)
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
    elif msg.channel.id == 741060207970615408:
        if msg.attachments:
            if len(msg.attachments) == 1:
                pic_ext = ['.jpg','.png','.jpeg', '.gif', '.mp4', '.mp3', '.webp']
                arcnombre = msg.attachments[0].filename.lower()
                for ext in pic_ext:
                    if arcnombre.endswith(ext):
                        await msg.add_reaction('✅')
                        await msg.add_reaction('❌')
            else:
                await msg.delete()
                pls = await msg.channel.send(f'{msg.author.mention}, sólo se puede enviar una imagen a la vez o de lo contratrio no podrán votar de manera correcta.')
                await asyncio.sleep(3)
                await pls.delete()

@bot.command(aliases=['confesión', 'confesion', 'confieso'])
async def confesar(ctx, *, texto : str = None):
    if texto == None:
        er = await ctx.send(f'{ctx.message.author.mention} Debes poner tu confesión `rpg>confesar <texto>`')
        await asyncio.sleep(3)
        await er.delete()
    else:
        canal = bot.get_channel(727172284250456137)
        con = discord.Embed(
            title=f'{ctx.message.author.name}',
            color = discord.Colour.blue()
        )
        con.set_thumbnail(
            url=ctx.message.author.avatar_url
        )
        con.add_field(
            name="Confesó",
            value=texto,
            inline=False
        )
        await canal.send(embed=con)
        await ctx.message.delete()

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
    violet = await bot.get_channel(735917504521830431).fetch_message(735938304356384859)
    dummer = await bot.get_channel(735917504521830431).fetch_message(740247414136373257)
    video_channel = bot.get_channel(726910405116690494)
    nuev = [1, 2, 3, 4]
    json_url = get(url[0])
    data = json.loads(json_url.text)
    json_url = get(url[1])
    data2 = json.loads(json_url.text)

    try:
        nuev[0] = int(data["items"][0]["statistics"]["subscriberCount"])
        nuev[1] = int(data["items"][0]["statistics"]["videoCount"])
        nuev[2] = int(data2["items"][0]["statistics"]["subscriberCount"])
        nuev[3] = int(data2["items"][0]["statistics"]["videoCount"])
    except:
        await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Límite de consultas exdidas :\'v.')
        subcount.cancel()

    #Subs de Violet Ink Band
    if ant[0] != nuev[0]:
        subs = getsubs(ant[0], nuev[0])
        await violet.edit(content=subs[0])
        if isinstance(subs[1], int):
            await bot.get_channel(726910120839086261).send(f'@everyone **Violet Ink Band** ha llegado a los **{subs[1]}** subscriptores, muchas gracias :metal::stuck_out_tongue_winking_eye:.')
        ant[0] = nuev[0]

    #Subs de Dummer
    if ant[2] != nuev[2]:
        subs = getsubs(ant[2], nuev[2])
        await dummer.edit(content=subs[0])
        if isinstance(subs[1], int):
            await bot.get_channel(726910120839086261).send(f'@everyone **Magical_Drummer** ha llegado a los **{subs[1]}** subscriptores, muchas gracias :UwU:.')
        ant[2] = nuev[2]

    #Avisos de nuevos vídeos de Violet Ink Band
    if nuev[1] > ant[1]:
        idvideos = getvideos(violet_idchannel, (nuev[1]-ant[1]))
        if idvideos[0] == None:
            await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Ocurrió un error al intentar avisar de nuevos vídeos:\n{idvideos[1]}.')
            subcount.cancel()
        else:
            for a in idvideos:
                if a != "No":
                    video_spam = await video_channel.send(f'@everyone ¡**Violet Ink Band** ha subido un nuevo vídeo! ¡Ve a verlo! https://www.youtube.com/watch?v={a}')
                    await video_spam.add_reaction('👍')
        ant[1] = nuev[1]
    elif nuev[1] < ant[1]:
        ant[1] = nuev[1]

    #Avisos de nuevos vídeos de Dummer
    if nuev[3] > ant[3]:
        idvideos = getvideos(dummer_idcahnnel, (nuev[3]-ant[3]))
        if idvideos[0] == None:
            await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Ocurrió un error al intentar avisar de nuevos vídeos:\n{idvideos[1]}.')
            subcount.cancel()
        else:
            for a in idvideos:
                if a != "No":
                    video_spam = await video_channel.send(f'@everyone ¡**Magical_Drummer** ha subido un nuevo vídeo! ¡Ve a verlo! https://www.youtube.com/watch?v={a}')
                    await video_spam.add_reaction('👍')
        ant[3] = nuev[3]
    elif nuev[3] < ant[3]:
        ant[3] = nuev[3]

def getsubs(ant : int, aho : int):
    numeros = [1, "No"]
    contenido = ""
    n = str(aho)
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
    numeros[0] = contenido
    meta = pow(10, len(n)-1)
    if meta <= aho and ant < meta:
        numeros[1] = meta
    return numeros

def getvideos(canal : str, cant : int):
    videos = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={canal}&part=id&order=date&maxResults={cant}'
    hoy = str(date.today().strftime('%Y-%m-%d'))
    json_url = get(videos)
    data = json.loads(json_url.text)
    idvideos = ["No"]
    for a in range(cant):
        try:
            idvideos.append(data["items"][a]["id"]["videoId"])
            json_url = get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={idvideos[a+1]}&key={api_key}')
            video_data = json.loads(json_url.text)
            fecha_vid = video_data["items"][0]["snippet"]["publishedAt"]
            fecha_vid = fecha_vid[:10]
            z = True
            x = 1
            while z:
                if hoy == fecha_vid:
                    print("sí")
                    z = False
                else:
                    sleep(20)
                    videos = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={canal}&part=id&order=date&maxResults={cant}'
                    json_url = get(videos)
                    data = json.loads(json_url.text)
                    idvideos[a+1] = data["items"][a]["id"]["videoId"]
                    json_url = get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={idvideos[a+1]}&key={api_key}')
                    video_data = json.loads(json_url.text)
                    fecha_vid = str(video_data["items"]["snippet"]["publishedAt"][:10])
                if x == 5 and z:
                    z == False
                    idvideos[0] = None
                    idvideos[1] = "Simplemente no se pudo"
                    print(str(hoy))
                    print(fecha_vid)
        except error:
            idvideos[0] = None
            if len(idvideos) > 1:
                idvideos[1] = error
            else:
                idvideos.append(error)
            break
    return idvideos

for filename in listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

#Token del bot
bot.run(getenv("DISCORD_SECRET_KEY"))
#bot.run(getenv("prueba_bot"))