import discord
import logging
import time
from discord.ext import commands, tasks
from config import TOKEN, CHAT_ROOM_ID, RIOT_IDS
from main import get_profile_data, get_match_data
from match_summary import create_match_summary, get_match_latest_id

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Set up the bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    check_lasted_match.start()
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

tft_run_var=False
@bot.command(name='tft_run')
async def tft_run(ctx):
    global tft_run_var
    if tft_run_var:
        tft_run_var=False
        await ctx.send("Stop running TFT match detection")
    else:
        tft_run_var=True
        await ctx.send("Start running TFT match detection")

@bot.command(name='tft')
async def tft_latest_match(ctx, riot_id: str, tag: str):
    try:
        profile_data = get_profile_data(riot_id, tag)
        if not profile_data:
            await ctx.send("Failed to retrieve profile data. Please try again later.")
            return

        match_id = get_match_latest_id(profile_data)
        print(match_id)
        if not match_id:
            await ctx.send("No recent matches found for this player.")
            return

        match_data = get_match_data(match_id, riot_id, tag)
        if not match_data:
            await ctx.send("Failed to retrieve match data. Please try again later.")
            return

        image_name = create_match_summary(profile_data, match_data)

        
        if image_name:
            with open(image_name, 'rb') as file:
                await ctx.send(file=discord.File(file, image_name))
        else:
            await ctx.send("Failed to generate match summary image.")
            
    except KeyError as e:
        logger.error(f"Missing key in match data: {e}")
        await ctx.send("Failed to retrieve match data. Some information is missing.")
    except Exception as e:
        logger.error(f"Error fetching match data: {e}")
        await ctx.send("Failed to retrieve match data. Please try again later.")
    
@tasks.loop(minutes=1)
async def check_lasted_match():
    if not tft_run_var:
        return False
    riot_ids=RIOT_IDS
    # Send the banner image file to Discord
    channel = bot.get_channel(CHAT_ROOM_ID)  # Replace with your channel ID
    if riot_ids == None:
        return False
    for i in riot_ids:
        riot_id, tag = i.split('#')

        try:
            
            # Fetch profile data
            profile_data = get_profile_data(riot_id, tag)
            if not profile_data:
                await channel.send("Failed to retrieve profile data. Please try again later.")
                return

            match_id = get_match_latest_id(profile_data)
            print(match_id)
            if not match_id:
                await channel.send("No recent matches found for this player.")
                return

            match_data = get_match_data(match_id, riot_id, tag)
            if not match_data:
                await channel.send("Failed to retrieve match data. Please try again later.")
                return

            image_name = create_match_summary(profile_data, match_data,shcedule_run=True)
            
            if image_name:
                # send message with image
                msg=f'Detect {i}'+'\'s latest match'
                with open(image_name, 'rb') as file:
                    await channel.send(file=discord.File(file, image_name),content=msg)
            else:
                continue

            


                
        except KeyError as e:
            logger.error(f"Missing key in match data: {e}")
            await channel.send("Failed to retrieve match data. Some information is missing.")
        except Exception as e:
            logger.error(f"Error fetching match data: {e}")
            await channel.send("Failed to retrieve match data. Please try again later.")
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
