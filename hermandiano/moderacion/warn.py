from hermandiano import Datos, bot
from . import permiso, advertir, revision, fecha_formato, mod_embed, canal_moderador, segundo_hilo, silenciar_tban
from discord.ext import commands
import discord
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor as hilo

@bot.command(aliases=["advertir"])
async def warn(ctx : commands.Context, member : discord.Member = None, *, razon : str = "Sin especificar"):
    server_id = str(ctx.message.guild.id)
    server_conf = Datos.get("servers/"+server_id+"/configs")
    idioma = server_conf["idioma"]

    if permiso(ctx.author, server_conf):
        compro_de_datos = True #True = Todos los datos están bien
        moderador = ctx.author

        if member == None:
            compro_de_datos = False
            await advertir(idioma, 39, ctx)
        else:
            compro_de_datos = await revision(member, ctx, server_conf, idioma)

        if compro_de_datos:
            member_id = str(member.id)
            idioma = server_conf["idioma"]

            hoy = datetime.today()

            #Revisa si el miembro existe en la base de datos y si ya tiene avisos previos
            avisos = Datos.get(f"servers/{server_id}/miembros/{member_id}/avisos")
            avisos_cant = 0
            if avisos != None:
                avisos_cant = len(avisos)
            else:
                avisos = []

            #Nuevo aviso
            aviso = {
                str(avisos_cant):{
                    "por": str(moderador.id),
                    "razon": razon,
                    "fecha": hoy.strftime(fecha_formato)
                }
            }

            Datos.update(f"servers/{server_id}/miembros/{member_id}/avisos",  aviso)
            embed_mod = mod_embed(moderador, member.mention, 1, idioma, 45, razon)
            await canal_moderador(server_conf, embed=embed_mod)

            avisos.append(aviso[str(avisos_cant)])
            
            #En caso de que se hayan configurados los castigos
            castigos = Datos.get(f"servers/{server_id}/castigos")
            if castigos != None:
                castigos_aplicar = []
                cant_avisos = len(avisos)-1
                castigos_aplicados = Datos.get(f"servers/{server_id}/miembros/{member_id}/castigos aplicados")
                for c in castigos:
                    castigo = castigos[c]
                    """Los castigos son activados según 3 factores: La cantidad de avisos hechos,
                    hace cuanto fue advertido al miembro y si ese castigo ya ha sido aplicado en
                    un cierto periodo de tiempo."""

                    if castigos["cant_warns"] <= cant_avisos:
                        seguir = True
                        #Revisa si el miembro tiene suficientes advertencias
                        if castigos_aplicados != None:
                            if c in castigos_aplicados:
                                ult_apl_cast = datetime.strptime(castigos_aplicados[c], fecha_formato)
                                #Revisa si al usuario ya se le ha aplicado el castigo en el tiempo del cooldown
                                if (hoy - ult_apl_cast).days < castigo["cooldown"]:
                                    seguir = False

                        #Revisa si la cantidad de advertencias se hicieron en el periodo de aplicación del castigo
                        if seguir:
                            aviso_ver = avisos[cant_avisos-castigo["cant_warns"]]
                            aviso_fecha = datetime.strptime(aviso_ver["fecha"], "%d/%m/%Y %H:%M")
                            tiempo_ad = castigo["tiempo_ad"]["dias"]*24*60*60
                            tiempo_ad += castigo["tiempo_ad"]["horas"]*60*60
                            fecha_ver = hoy - timedelta(seconds=tiempo_ad)
                            if fecha_ver >= aviso_fecha:
                                seguir = True
                        
                        if seguir:
                            role = None
                            if "role_silencio" in server_conf:
                                try:
                                    role = bot.get_guild(int(server_id)).get_role(int(server_conf["role_silencio"]))
                                except discord.NotFound:
                                    pass
                            tiempo = castigo["dura"]["dias"]*24*60*60
                            tiempo += castigo["dura"]["horas"]*60*60
                            tiempo += castigo["dura"]["minutos"]*60
                            parametros = {
                                "member": member,
                                "tiempo": tiempo,
                                "role": role
                            }

                            informacion = f"El miembro {member.mention} fue "
                            accion = None
                            if castigo["castigo"] == 2:
                                informacion += "silenciado por "
                                parametros["sil_tban"] = True
                            elif castigo["castigo"] == 3:
                                informacion += "baneado por "
                                parametros["sil_tban"] = False
                            elif castigo["castigo"] == 4:
                                informacion += "expulsado por "
                                accion = member.kick
                            elif castigo["castigo"] == 5:
                                informacion += "baneado permantentemente "
                                accion = member.ban
                            
                            if castigo["castigo"] < 4:
                                informacion += castigo["dura"]["dias"]+" día(s) "
                                informacion += castigo["dura"]["horas"]+" horas y "
                                informacion += castigo["dura"]["minutos"]+" minútos "
                                
                            informacion += "por acumular "+castigo["cant_warns"]+" advertencias en menos de "
                            informacion += castigo["tiempo_ad"]["dias"]+" día(s) y "
                            informacion += castigo["tiempo_ad"]["horas"]+" horas"

                            if castigo["castigo"] < 4:
                                hilo().submit(segundo_hilo, args=[True, silenciar_tban, None, parametros])
                            else:
                                await accion(reason=informacion)
                            
                            Datos.update(f"servers/{server_id}/members/{member_id}/castigos aplicados", {c:hoy.strftime(fecha_formato)})
                            member_castigos = Datos.get(f"servers/{server_id}/members/{member_id}/castigos")
                            Datos.update(f"servers/{server_id}/members/{member_id}/castigos", {
                                str(len(member_castigos)):{
                                    "id": c,
                                    "fecha": hoy.strftime(fecha_formato),
                                    "informacion": informacion
                                }
                            })
                            embed_mod = mod_embed(moderador, member.mention, castigo["castigo"], idioma, 46, informacion)
                            await canal_moderador(server_conf, embed=embed_mod)

    else:
        await advertir(idioma, 5, ctx)