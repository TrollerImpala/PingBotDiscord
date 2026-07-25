import discord
from discord import app_commands
from discord.ext import commands

from threading import Thread
from flask import Flask

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

import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='-&', intents=intents)

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

@bot.event
async def on_ready():
    print("Bot ping conectado")

    try:
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
    inter_id = interaction.guild_id

    configuraciones[inter_id] = {
        "rol" : rol.id,
        "canal" : canal.id,
        "bot" : bot_trigger.id,
        "msg" : msg
    }

    guardar_configuracion(configuraciones)

    await interaction.response.send_message(

        f"✅ **Configuración guardada correctamente:**\n"
        f"• **Canal:** {canal.mention}\n"
        f"• **Bot:** {bot_trigger.mention}\n"
        f"• **Rol a mencionar:** {rol.mention}\n"
        f"• **Mensaje:** {msg}"
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
        config = configuraciones[message.guild.id]

        if message.author.id == config['bot'] and message.channel.id == config['canal']:
            await message.channel.send(f"<@&{config['rol']}> {config['msg']}")

    await bot.process_commands(message)


bot.run(os.getenv('TOKEN'))

