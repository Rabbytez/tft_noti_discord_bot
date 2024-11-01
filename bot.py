import discord
import logging
import asyncio
from discord.ext import commands
from config import TOKEN, CHAT_ROOM_ID
from main import get_tft_profile, format_latest_match_for_discord  # Import functions from main.py
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Set up the bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

@bot.event
async def on_disconnect():
    logger.warning("Bot disconnected. Attempting to reconnect...")

@bot.command(name='vt')
async def join_voice(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send(f"Joined {channel}")
            logger.info(f"Connected to voice channel: {channel}")
        else:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"Moved to {channel}")
            logger.info(f"Moved to voice channel: {channel}")
    else:
        await ctx.send("You are not connected to a voice channel.")

@bot.command(name='tft')
async def latest_match(ctx, riot_id: str, tag: str):
    try:
        profile_data = get_tft_profile(riot_id, tag)
        discord_message = format_latest_match_for_discord(profile_data)
        await ctx.send(discord_message)
    except Exception as e:
        logger.error(f"Error fetching match data: {e}")
        await ctx.send("Failed to retrieve match data. Please try again later.")

def run_bot():
    reconnect_attempts = 0
    max_attempts = 5
    while reconnect_attempts < max_attempts:
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            logger.error("Invalid token. Check your token.")
            break
        except Exception as e:
            reconnect_attempts += 1
            logger.error(f"Error occurred: {e}. Reconnect attempt {reconnect_attempts} of {max_attempts}.")
            time.sleep(min(5 * reconnect_attempts, 30))  # Progressive delay up to 30 seconds
        else:
            reconnect_attempts = 0  # Reset after a successful connection

if __name__ == "__main__":
    run_bot()