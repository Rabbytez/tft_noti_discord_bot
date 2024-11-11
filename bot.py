import discord
import logging
import time
from discord.ext import commands, tasks
from config import TOKEN, CHAT_ROOM_ID,RIOT_IDS
from main import get_profile_data
from match_summary import create_match_summary

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
    chech_lasted_match.start()

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
        # Fetch profile data
        profile_data = get_profile_data(riot_id, tag)

        # Check for the presence of 'summoner' and 'matches' keys
        if 'summoner' not in profile_data:
            await ctx.send("No summoner data found for this player. Please check the Riot ID and tag.")
            logger.error("Missing 'summoner' key in profile data.")
            return
        
        if 'matches' not in profile_data or not profile_data['matches']:
            await ctx.send("No match data available for this player.")
            logger.error("Missing 'matches' key or no matches in profile data.")
            return
        
        # Get the latest match by timestamp
        latest_match = max(profile_data["matches"], key=lambda x: x.get("match_timestamp", 0))

        # Generate the match summary banner using HTML and capture it as an image
        image_name=create_match_summary(profile_data)
        
        # Send the banner image file to Discord
        with open(image_name, 'rb') as file:
            await ctx.send(file=discord.File(file, image_name))
            
    except KeyError as e:
        logger.error(f"Missing key in match data: {e}")
        await ctx.send("Failed to retrieve match data. Some information is missing.")
    except Exception as e:
        logger.error(f"Error fetching match data: {e}")
        await ctx.send("Failed to retrieve match data. Please try again later.")

@tasks.loop(minutes=1)
async def chech_lasted_match():

    riot_ids=RIOT_IDS
    if riot_ids == None:
        return False
    for i in riot_ids:
        riot_id, tag = i.split('#')

        try:
            # Fetch profile data
            profile_data = get_profile_data(riot_id, tag)

            # Generate the match summary banner using HTML and capture it as an image
            image_name=create_match_summary(profile_data,True)
            
            if image_name == False:
                continue
            # Send the banner image file to Discord
            channel = bot.get_channel(CHAT_ROOM_ID)  # Replace with your channel ID
            
            # send message with image
            msg=f'Detect {i}'+'\'s latest match'
            with open(image_name, 'rb') as file:
                await channel.send(file=discord.File(file, image_name),content=msg)

                
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
