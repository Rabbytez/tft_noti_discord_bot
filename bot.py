import discord
import logging
import time
from discord.ext import commands, tasks
from config import TOKEN, CHAT_ROOM_ID,RIOT_IDS
from main import get_tft_profile, create_match_summary , show_match_detail, generate_match_rounds_report, show_win_rate_graph , get_latest_match_data

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

@bot.command(name='start_check')
async def start_check(ctx):
    if check_lasted_match.is_running():
        await ctx.send("The match checking task is already running.")
    else:
        check_lasted_match.start()
        await ctx.send("Started the match checking task.")

@bot.command(name='stop_check')
async def stop_check(ctx):
    if check_lasted_match.is_running():
        check_lasted_match.cancel()
        await ctx.send("Stopped the match checking task.")
    else:
        await ctx.send("The match checking task is not running.")

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

# Global dictionary to store message IDs and associated riot_id and tag
message_riot_data = {}

@bot.command(name='tft')
async def latest_match(ctx, riot_id: str, tag: str):
    try:
        # Fetch profile data
        profile_data = get_tft_profile(riot_id, tag)

        # Check for the presence of 'summoner' and 'matches' keys
        if 'summoner' not in profile_data:
            await ctx.send("No summoner data found for this player. Please check the Riot ID and tag.")
            logger.error("Missing 'summoner' key in profile_data.")
            return
        
        if 'matches' not in profile_data or not profile_data['matches']:
            await ctx.send("No match data available for this player.")
            logger.error("Missing 'matches' key or no matches in profile_data.")
            return
        
        # Generate the match summary banner using HTML and capture it as an image
        image_name = create_match_summary(profile_data)
        
        # Send the banner image file to Discord
        with open(image_name, 'rb') as file:
            message = await ctx.send(file=discord.File(file, image_name))

        # Store riot_id and tag associated with this message
        message_riot_data[message.id] = (riot_id, tag)

        # Add reactions for emoji interactions
        await message.add_reaction("📊")  # Match detail
        await message.add_reaction("📐")  # TFT unit layout and tribes
        await message.add_reaction("📈")  # Win rate per stage graph

    except Exception as e:
        logger.error(f"Error fetching match data: {e}")
        await ctx.send("Failed to retrieve match data. Please try again later.")

@tasks.loop(minutes=1)
async def check_lasted_match():
    riot_ids = RIOT_IDS
    if riot_ids is None:
        return

    for i in riot_ids:
        riot_id, tag = i.split('#')

        try:
            # Fetch profile data
            profile_data = get_tft_profile(riot_id, tag)

            # Generate the match summary banner using HTML and capture it as an image
            image_name = create_match_summary(profile_data, True)
            
            if image_name == False:
                continue

            # Send the banner image file to Discord
            channel = bot.get_channel(CHAT_ROOM_ID)
            msg = f"Detect {i}'s latest match"
            with open(image_name, 'rb') as file:
                message = await channel.send(file=discord.File(file, image_name), content=msg)

            # Store riot_id and tag associated with this message
            message_riot_data[message.id] = (riot_id, tag)

            # Add reactions for emoji interactions
            await message.add_reaction("📊")  # Match detail
            await message.add_reaction("📐")  # TFT unit layout and tribes
            await message.add_reaction("📈")  # Win rate per stage graph

        except KeyError as e:
            logger.error(f"Missing key in match data: {e}")
            await channel.send("Failed to retrieve match data. Some information is missing.")
        except Exception as e:
            logger.error(f"Error fetching match data: {e}")
            await channel.send("Failed to retrieve match data. Please try again later.")

@bot.event
async def on_reaction_add(reaction, user):
    global message_riot_data  # Declare global variable
    if user == bot.user:
        return

    try:
        message_id = reaction.message.id
        if message_id in message_riot_data:
            riot_id, tag = message_riot_data[message_id]
        else:
            await reaction.message.channel.send(f"{user.mention}, no associated data found for this message.")
            return

        # Fetch profile data and latest match data
        profile_data = get_tft_profile(riot_id, tag)
        latest_match_data = get_latest_match_data(profile_data)

        if reaction.emoji == "📊":
            # Generate player stats image
            player_stats_image = show_match_detail(profile_data)
            await reaction.message.channel.send(file=discord.File(player_stats_image, 'match_detail.png'))
        
        elif reaction.emoji == "📐":
            # Generate match rounds report as an image
            rounds_image = generate_match_rounds_report(riot_id, tag, profile_data)
            await reaction.message.channel.send(file=discord.File(rounds_image, 'match_rounds.png'))
        
        elif reaction.emoji == "📈":
            # Generate win rate graph
            win_rate_graph = show_win_rate_graph()
            await reaction.message.channel.send(file=discord.File(win_rate_graph, 'win_rate_graph.png'))

        # Optional cleanup
        message_riot_data.pop(message_id, None)

    except Exception as e:
        logger.exception(f"Error processing reaction {reaction.emoji}")
        await reaction.message.channel.send(f"{user.mention}, there was an error processing your request. Please try again later.")

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