import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHAT_ROOM_ID = int(os.getenv('CHAT_ROOM_ID'))
