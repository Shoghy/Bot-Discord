from . import permiso, advertir, revision, fecha_formato, segundo_hilo, mod_embed, silenciar_tban
from hermandiano import bot, Datos, bot_i
from datetime import datetime
from typing import Union
from discord.ext import commands
import discord
from concurrent.futures import ThreadPoolExecutor as hilo

@bot.command()
async def tempmute(ctx : Union[commands.Context, discord.ApplicationContext], member : discord.Member = None, tiempo : int = 0, *, razon : str = "Sin especificar"):
    server_id = str(ctx.message.guild.id)
    server_conf = Datos.get("servers/"+server_id+"/configs")
    idioma = server_conf["idioma"]

    if permiso(ctx.author, server_conf):
        compro_de_datos = True #True = Todos los datos están bien
        moderador = ctx.author
        member_id = str(member.id)

        if member == None:
            compro_de_datos = False
            await advertir(idioma, 39, ctx)
        else:
            compro_de_datos = await revision(member, ctx, server_conf, idioma)

        if tiempo <= 0 or tiempo > 180:
            compro_de_datos = False
            await advertir(idioma, 54, ctx)

        if compro_de_datos:
            try:
                await member.edit(mute=True)
            except discord.errors.HTTPException:
                pass

            member_data = Datos.get("servers/"+server_id+"/miembros/"+member_id)
            cast_mods = 0
            if member_data != None:
                if "castigos_mod" in member_data:
                    cast_mods = len(member_data["castigos_mod"])

            fecha = datetime.today().strftime(fecha_formato)
            cast_data = {
                str(cast_mods): {
                    "castigo": 2,
                    "por": str(moderador.id),
                    "razon": razon,
                    "fecha": fecha
                }
            }

            tiempo = 60 * tiempo
            role_s = None
            if "role_silencio" in server_conf:
                role_s = ctx.guild.get_role(int(server_conf["role_silencio"]))
            
            parametros = {
                "member": member,
                "tiempo": tiempo,
                "sil_tban": True,
                "role": role_s
            }
            hilo().submit(segundo_hilo, args=[True, silenciar_tban, None, parametros])
            #th(self.segundo_hilo, args=[True, self.silenciar_tban, None, parametros]).start()

            if member_data == None:
                Datos.set_data(f"servers/{server_id}/miembros/{member_id}", {"castigos_mod" : cast_data})
            else:
                if cast_mods == 0:
                    Datos.set_data(f"servers/{server_id}/miembros/{member_id}/castigos_mod", cast_data)
                else:
                    Datos.update(f"servers/{server_id}/miembros/{member_id}/castigos_mod", cast_data)

            if "mod_log" in server_conf:
                embed_mod = mod_embed(moderador, member, 2, idioma, 46, razon)
                min_str = 0
                if tiempo == 1:
                    min_str = f"{tiempo} Minuto"
                else:
                    min_str = f"{tiempo} Minutos"

                embed_mod.add_field(
                    name=str(bot_i.cell_value(54, idioma)),
                    value=min_str
                )
                canal = ctx.guild.get_channel(server_conf["mod_log"])
                await canal.send(embed=embed_mod)

    else:
        await advertir(idioma, 5, ctx)