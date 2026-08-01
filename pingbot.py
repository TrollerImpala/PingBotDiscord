import discord
from discord import app_commands
from discord.ext import commands

from threading import Thread
from flask import Flask

from supabase import Client, create_client
import os

app = Flask(__name__)

@app.route('/')
def home():
  return 'Bot activo 24/7'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = Thread(target=run)
  t.start()


keep_alive()

from dotenv import load_dotenv
load_dotenv()

#import json

url : str = os.getenv('SUPABASE_URL')
key : str = os.getenv('SUPABASE_KEY')

supabase : Client = create_client(url, key)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='-&', intents=intents)
"""
CONFIG_FILE = "config.json"

def cargar_configuracion():
    if not os.path.exists("config.json") or os.path.getsize("config.json") == 0:

        with open("config.json", "w", encoding="utf-8") as f:
            json.dump({}, f)
        
        return {}

    try:
        with open("config.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
            return {int(k): v for k, v in datos.items()}
        
    except (json.JSONDecodeError, Exception) as e:

        print(f"Error al cargar config.json: {e}")

        with open("config.json", "w", encoding="utf-8") as f:
            json.dump({}, f)

        return {}



def guardar_configuracion(configuraciones):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(configuraciones, file, indent=4)

    except Exception as e:
        print(f"Error al guardar {CONFIG_FILE}: {e}")


configuraciones = cargar_configuracion()

"""
configuraciones = {}

@bot.event
async def on_ready():
    print("Bot ping conectado")
    global configuraciones

    try:
        configuraciones.clear()
        
        res = supabase.table('config').select('*').execute()

        for item in res.data:
            guild_id = int(item['guild_id'])

            if guild_id not in configuraciones:
                configuraciones[guild_id] = []

            configuraciones[guild_id].append(item)
            
        #configuraciones = {int(item['guild_id']): item for item in res.data}

        sync = await bot.tree.sync()
        print(f'Comandos sincronizados {len(sync)}')

    except Exception as e:
        print(f"Error {e}")


@bot.tree.command(name='configurar')
@app_commands.checks.has_permissions(administrator=True)
async def configurar(
    interaction : discord.Interaction,
    rol : discord.Role,
    msg : str,
    canal : discord.TextChannel,
    bot_trigger : discord.User
):
#   inter_id = interaction.guild_id

#    configuraciones[inter_id] = {}

    #guardar_configuracion(configuraciones)

    datos_config = {
        "rol": str(rol.id),
        "canal": str(canal.id),
        "bot": str(bot_trigger.id),
        "msg": msg,
        "guild_id": str(interaction.guild_id)
    }

    try:
        res = supabase.table('config').insert( datos_config ).execute()

        registro = res.data[0] if res.data else datos_config

        if interaction.guild_id not in configuraciones:
            configuraciones[interaction.guild_id] = []
        
        configuraciones[interaction.guild_id].append(registro)
    
        await interaction.response.send_message(

            f"✅ **Configuración guardada correctamente:**\n"
            f"• **Canal:** {canal.mention}\n"
            f"• **Bot:** {bot_trigger.mention}\n"
            f"• **Rol a mencionar:** {rol.mention}\n"
            f"• **Mensaje:** {msg}"
        )
        
    except Exception as e:
        await interaction.response.send_message(
        f"**Error lol** : {e}",
        ephemeral = True
        )


@configurar.error
async def configurar_error(interaction : discord.Interaction, error):

    if isinstance(error, app_commands.MissingPermissions):

        await interaction.response.send_message(
            "q haces w 👀", 
            ephemeral=True
        )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.guild and message.guild.id in configuraciones:

        for config in configuraciones[message.guild.id]:
            if message.author.id == int(config['bot']) and message.channel.id == int(config['canal']):
                await message.channel.send(f"<@&{config['rol']}> {config['msg']}")

    await bot.process_commands(message)

bot.run(os.getenv('TOKEN'))

