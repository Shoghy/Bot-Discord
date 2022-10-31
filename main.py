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
from datetime import date
from time import sleep
from webserver import keep_alive

#Obtener los datos del archivo .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#Variables universales
api_key = getenv("GOOGLE_SECRET_KEY")
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
    if len(name) > 25:
        name_div = name.split()
        if len(name_div) > 1:
            if len(name_div[0]) < 25:
                nombre = ""
                nombre2 = ""
                for m in name_div:
                    if len(nombre+m) < 25:
                        if nombre == "":
                            nombre = m
                        else:
                            nombre = nombre+" "+m
                    else:
                        if nombre2 == "":
                            nombre2 = m
                        else:
                            nombre2 = nombre2+" "+m
                name = nombre+"\n"+nombre2
            else:
                name = name[:25]+"\n"+name[25:]
        else:
            name = name[:25]+"\n"+name[25:]
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

def leerjson():
    with open("cogs/personajes.json", 'r', encoding="utf-8") as contenido:
        jugador = json.load(contenido)
    return jugador

def escribirjson(jugador):
    with open("cogs/personajes.json", 'w', encoding="utf-8") as contenido:
        json.dump(jugador, contenido)

#Mensaje que se escribe cuando el bot ya está funcionando
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('0.1.2'))
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
    jsondoc = leerjson()
    canal = jsondoc["jugadores"][str(member.guild.id)]["configs"]["bienvenida_canal"]
    role = jsondoc["jugadores"][str(member.guild.id)]["configs"]["nuevo_usuario_role"]
    mensaje = jsondoc["jugadores"][str(member.guild.id)]["configs"]["mensaje_bienvenida"]
    mensaje = mensaje.replace("{user}", f"{member.mention}")
    mensaje = mensaje.replace("{server}", f"**{member.guild.name}**")
    if canal != None:
        try:
            channel = bot.get_channel(canal)
            imgdni(member.avatar_url, member.joined_at, member.display_name, member.id)
            file = discord.File(str(member.id)+".png")
            await channel.send(mensaje, file=file)
            remove(str(member.id)+".png")
        except:
            pass
    if role != None:
        try:
            roledeinicio = discord.utils.get(member.guild.roles, id=role)
            await member.add_roles(roledeinicio)
        except:
            pass

@bot.event
async def on_guild_join(guild):
    jsondoc = leerjson()
    jsondoc["jugadores"][str(guild.id)] = {}
    jsondoc["jugadores"][str(guild.id)]["configs"] = jsondoc["default_servers_config"]
    jsondoc["mensajes"][str(guild.id)] = {}
    escribirjson(jsondoc)

@bot.event
async def on_guild_remove(guild):
    jsondoc = leerjson()
    del jsondoc["jugadores"][str(guild.id)]
    del jsondoc["mensajes"][str(guild.id)]
    escribirjson(jsondoc)

@bot.event
async def on_member_remove(member):
    jsondoc = leerjson()
    canal = jsondoc["jugadores"][str(member.guild.id)]["configs"]["despedida_canal"]
    mensaje = jsondoc["jugadores"][str(member.guild.id)]["configs"]["mensaje_despedida"]
    mensaje = mensaje.replace("{user}", f"**{member.display_name}**")
    if str(member.id) in jsondoc["jugadores"][str(member.guild.id)]:
        del jsondoc["jugadores"][str(member.guild.id)][str(member.id)]
        escribirjson(jsondoc)
    if canal != None:
        try:
            channel = bot.get_channel(canal)
            despedida = await channel.send(mensaje)
            await despedida.add_reaction('👋')
        except:
            pass

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
            try:
                await ctx.message.delete()
            except discord.NotFound:
                pass
            no = await ctx.send(f'{ctx.message.author.mention}, No puedes usar el comando en este canal')
            await asyncio.sleep(3)
            try:
                await no.delete()
            except discord.NotFound:
                pass

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
    if ctx.author.guild_permissions.administrator:
        if cant != None and isinstance(cant, int):
            async for message in ctx.channel.history(limit=cant+1):
                try:
                    await message.delete()
                except discord.NotFound:
                    pass
            if cant != 1:
                listo = await ctx.send(f'He borrado `{cant} mensajes`.')
                await asyncio.sleep(3)
                try:
                    await listo.delete()
                except discord.NotFound:
                    pass
            else:
                listo = await ctx.send(f'He borrado `{cant} mensaje`.')
                await asyncio.sleep(3)
                try:
                    await listo.delete()
                except discord.NotFound:
                    pass
        else:
            er = await ctx.send(f'{ctx.message.author.mention} Debes poner la cantidad de mensajes que quieras borrar `rpg>clear <num>` y el número debe ser mayor a 0.')
            await asyncio.sleep(3)
            try:
                await er.delete()
            except discord.NotFound:
                pass
    else:
        adver = await ctx.send(f'{ctx.message.author.mention} No tienes permisos para usar este comando.')
        await asyncio.sleep(3)
        try:
            await adver.delete()
        except discord.NotFound:
            pass

@bot.event
async def on_message(msg):
    await bot.process_commands(msg)
    jsondoc = leerjson()
    if str(msg.channel.id) in jsondoc["jugadores"][str(msg.guild.id)]["configs"]["canales_de_memes"]:
        if jsondoc["jugadores"][str(msg.guild.id)]["configs"]["canales_de_memes"][str(msg.channel.id)]:
            if msg.attachments:
                pic_ext = ['.jpg','.png','.jpeg', '.gif', '.mp4', '.mp3', '.webp']
                arcnombre = msg.attachments[0].filename.lower()
                for ext in pic_ext:
                    if arcnombre.endswith(ext):
                        await msg.add_reaction('👍')
                        await msg.add_reaction('👎')

"""@bot.command(aliases=['confesión', 'confesion', 'confieso'])
async def confesar(ctx, *, texto : str = None):
    if texto == None:
        er = await ctx.send(f'{ctx.message.author.mention} Debes poner tu confesión `rpg>confesar <texto>`')
        await asyncio.sleep(3)
        try:
            await er.delete()
        except discord.NotFound:
            pass
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
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass"""

#Mensaje de error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        msgerror = await ctx.send(f'{ctx.message.author.mention} Comando inexistente.')
        await asyncio.sleep(3)
        try:
            await msgerror.delete()
        except discord.NotFound:
            pass
    else:
        await bot.get_channel(736207259327266881).send(f'{bot.get_user(345737329383571459).mention} Ocurrió un error:\n{error}')

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
                    fecha_vid = str(video_data["items"][0]["snippet"]["publishedAt"])[:10]
                if x == 5 and z:
                    z == False
                    idvideos[0] = None
                    idvideos[1] = "Simplemente no se pudo"
                    print(str(hoy))
                    print(fecha_vid)
        except:
            idvideos[0] = None
            if len(idvideos) > 1:
                idvideos[1] = sys.exc_info()[0]
            else:
                idvideos.append(sys.exc_info()[0])
            break
    return idvideos

for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

#Token del bot
keep_alive()
bot.run(getenv("DISCORD_SECRET_KEY"))
#bot.run(getenv("prueba_bot"))