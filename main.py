import requests
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from jinja2 import Template
from augments import augment_data
from json_create_dict import organize_stage_data
import time
import matplotlib.pyplot as plt
import glob
import random

folder_path = "outputs/"


def get_tft_profile(riot_id, tag, tft_set="TFTSet12", include_revival_matches=False):
    base_url = "https://api.metatft.com/public/profile/lookup_by_riotid"
    path = f"/TH2/{riot_id}/{tag}"
    params = {
        "source": "full_profile",
        "tft_set": tft_set,
        "include_revival_matches": str(include_revival_matches).lower(),
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.metatft.com",
        "Referer": "https://www.metatft.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }
    refresh_url = f"https://api.metatft.com/public/profile/refresh_by_riotid/TH2/{riot_id}/{tag}?tier=1"
    requests.post(f"{refresh_url}", headers=headers)

    response = requests.get(f"{base_url}{path}", headers=headers, params=params)

    if response.status_code == 200:
        try:
            data = response.json()  # Parse JSON here
        except json.JSONDecodeError:
            print("Failed to parse JSON from response.")
            return None
        save_json_to_file(data, folder_path, f"{riot_id}_{tag}_profile.json")
        return data
    else:
        response.raise_for_status()


def get_tft_unit_items_processed():
    base_url = "https://api2.metatft.com/tft-comps-api/unit_items_processed"

    response = requests.get(base_url)

    if response.status_code == 200:
        try:
            data = response.json()
            # Save the data to a JSON file
            folder_path = "outputs"  # Ensure this path exists
            save_json_to_file(data, folder_path, f"unit_items_processed.json")
            return data
        except json.JSONDecodeError:
            print("Error: Response is not valid JSON.")
            print(
                "Response content:", response.content
            )  # Print raw content for debugging
    else:
        print(f"Error: Received status code {response.status_code}")
        print("Response content:", response.content)  # Print raw content for debugging


def get_tft_percentiles():
    base_url = "https://api2.metatft.com/tft-stat-api/percentiles"

    response = requests.get(base_url)

    if response.status_code == 200:
        try:
            data = response.json()
            # Save the data to a JSON file
            folder_path = "outputs"  # Ensure this path exists
            save_json_to_file(data, folder_path, f"tft_percentiles.json")
            return data
        except json.JSONDecodeError:
            print("Error: Response is not valid JSON.")
            print(
                "Response content:", response.content
            )  # Print raw content for debugging
    else:
        print(f"Error: Received status code {response.status_code}")
        print("Response content:", response.content)  # Print raw content for debugging


def save_json_to_file(data, folder_path, file_name):
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {file_path}")


def get_meme_url_by_placement(placement):
    # Define the meme URLs based on placement
    meme_urls = {
        1: "https://api.memegen.link/images/stonks.png",
        2: "https://api.memegen.link/images/cheems/it's_gooood.jpg",
        3: "https://api.memegen.link/images/fine/this_is_fine.jpg",
        4: "https://api.memegen.link/images/grave/_/5th_place/4th_place.jpg",
        5: "https://api.memegen.link/images/ugandanknuck/5th_place/it's_okay_just_10_lp.png",
        6: "https://api.memegen.link/images/disastergirl/7th_place/me.jpg",
        7: "https://api.memegen.link/images/ds/7th_place/8th_place.png",
        8: "https://api.memegen.link/images/buzz/you_see_that/you_are_at_the_bottom.png",
        9: "https://api.memegen.link/images/woman-cat/why_is_it_not_working/error.jpg",
    }
    # Return the meme URL based on placement, default to the last meme if not found
    return meme_urls.get(placement, meme_urls[9])


rank_data = {
    "Iron": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/iron.png",
        "color": "#6d6d6d",  # Grey for Iron
    },
    "Bronze": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/bronze.png",
        "color": "#cd7f32",  # Bronze color
    },
    "Silver": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/silver.png",
        "color": "#c0c0c0",  # Silver color
    },
    "Gold": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/gold.png",
        "color": "#ffd700",  # Gold color
    },
    "Platinum": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/platinum.png",
        "color": "#00ff00",  # Green for Platinum
    },
    "Emerald": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/emerald.png",
        "color": "#2ecc71",  # Emerald green
    },
    "Diamond": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/diamond.png",
        "color": "#00c8ff",  # Blue for Diamond
    },
    "Master": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/master.png",
        "color": "#ff00ff",  # Purple for Master
    },
    "GrandMaster": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/grandmaster.png",
        "color": "#ff4500",  # Red-orange for GrandMaster
    },
    "Challenger": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/challenger.png",
        "color": "#ff6347",  # Tomato color for Challenger
    },
}


# Function to get rank icon and color
def get_rank_icon_and_color(rating_text):
    # Split rank and tier from the rating text
    rank = rating_text.split(" ")[0]  # e.g., "EMERALD"
    rank_roman = " ".join(rating_text.split(" ")[1:])  # Join the rest of the parts
    # Get rank data if it exists, otherwise default to unranked settings
    rank_info = rank_data.get(
        rank.capitalize(), {"icon": "", "color": "#ffffff"}
    )  # Default to white if rank not found
    return rank_info["icon"], rank_info["color"], rank_roman


def get_lp_change_color(lp_change):
    """Return a CSS class based on LP change."""
    return "green" if lp_change > 0 else "red"


def format_time_elapsed(seconds):
    """Convert seconds into a human-readable format."""
    days, seconds = divmod(seconds, 86400)  # 86400 seconds in a day
    hours, seconds = divmod(seconds, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(seconds, 60)  # 60 seconds in a minute

    time_components = []
    if days > 0:
        time_components.append(f"{int(days)}d")
    if hours > 0:
        time_components.append(f"{int(hours)}h")
    if minutes > 0:
        time_components.append(f"{int(minutes)}m")
    if seconds > 0 or not time_components:
        time_components.append(f"{int(seconds)}s")

    return " ".join(time_components) + " ago"


def create_match_summary(profile_data, shcedule_run=False):
    # Extract relevant data from profile_data
    summoner = profile_data.get("summoner", {})
    ranked = profile_data.get("ranked", {})
    latest_match = profile_data.get("matches", [{}])[
        0
    ]  # Assuming latest match is the first

    tacticians_icon = latest_match.get("summary", {}).get("little_legend", "")
    summoner_icon = summoner.get("profile_icon_id", "")
    latest_match_id = latest_match.get("riot_match_id", "")
    puid = summoner.get("puuid", "")
    # check last match id of this user(puid) on file if it is the same as the latest match id abort
    if shcedule_run:
        # example of json
        # {
        #     "puid": "latest_match_id"
        # }
        if not os.path.exists("last_match_id.json"):
            with open("last_match_id.json", "w") as json_file:
                json.dump({}, json_file)

        with open("last_match_id.json") as json_file:
            last_match_id = json.load(json_file)
            last_match_id_json = last_match_id

        if puid not in last_match_id_json:
            # print('puid not in last_match_id_json')
            last_match_id_json.update({puid: latest_match_id})
            with open("last_match_id.json", "w") as json_file:
                json.dump(last_match_id_json, json_file)

        else:
            # print('puid in last_match_id_json')
            if last_match_id_json[puid] == latest_match_id:
                return False
            else:
                last_match_id_json[puid] = latest_match_id
                with open("last_match_id.json", "w") as json_file:
                    json.dump(last_match_id, json_file)

    unit_tier = latest_match.get("summary", {}).get("units", [{}])[0].get("tier", 0)

    # Calculate time elapsed since the match
    current_time = time.time()
    match_timestamp = latest_match.get("match_timestamp", current_time)

    # Check if the timestamp is in milliseconds and convert to seconds if necessary
    if (
        match_timestamp > 1e12
    ):  # If the timestamp is too large, it's likely in milliseconds
        match_timestamp /= 1000

    time_elapsed = current_time - match_timestamp

    # Handle negative time_elapsed
    if time_elapsed < 0:
        time_elapsed = 0  # Set to zero if the match timestamp is in the future

    # Format the elapsed time into a human-readable format
    time_elapsed_formatted = format_time_elapsed(time_elapsed)

    # Use .get() to safely access 'time_eliminated'
    time_eliminated = latest_match.get("summary", {}).get(
        "time_eliminated", 0
    )  # Default to 0 if not found
    time_eliminated_formatted = (
        f"{int(time_eliminated // 60)}m {int(time_eliminated % 60)}s"
    )

    ranked_rating_text = ranked.get("rating_text", "Unranked")
    rank_name = ranked_rating_text.split(" ")[0]  # Extract the rank name
    rank_icon_url, rank_color, rank_roman = get_rank_icon_and_color(ranked_rating_text)

    latest_augments = latest_match.get("summary", {}).get("augments", [])
    augment_urls = [augment_data(i) for i in latest_augments]

    player_rating_text = latest_match.get("summary", {}).get(
        "player_rating_numeric", ""
    )
    ranked_rating_text = ranked.get("rating_numeric", "")

    try:
        print(player_rating_text)
        print(ranked_rating_text)
        lp_difference = int(ranked_rating_text) - int(player_rating_text)
    except:
        lp_difference = 0

    # Get the meme URL based on placement
    meme_image = get_meme_url_by_placement(latest_match.get("placement", 9))

    stats = {
        "username": summoner.get("riot_id", "").split("#")[0],
        "tag": summoner.get("riot_id", "").split("#")[1],
        "time": time_elapsed_formatted,
        "duration": time_eliminated_formatted,
        "lp_change": f"{'-' if lp_difference < 0 else '+'}{abs(lp_difference)} LP",
        "lp_change_color": get_lp_change_color(lp_difference),  # Determine color
        "rank_icon": rank_icon_url,
        "rank_color": rank_color,
        "rank": rank_name,
        "rank_roman": rank_roman,
        "augment_urls": augment_urls,
    }

    champion_assets = {
        "Ashe": {
            "url": "https://rerollcdn.com/characters/Skin/12/Ashe.png",
            "price": 1,
        },
        "Blitzcrank": {
            "url": "https://rerollcdn.com/characters/Skin/12/Blitzcrank.png",
            "price": 1,
        },
        "Elise": {
            "url": "https://rerollcdn.com/characters/Skin/12/Elise.png",
            "price": 1,
        },
        "Jax": {"url": "https://rerollcdn.com/characters/Skin/12/Jax.png", "price": 1},
        "Jayce": {
            "url": "https://rerollcdn.com/characters/Skin/12/Jayce.png",
            "price": 1,
        },
        "Lillia": {
            "url": "https://rerollcdn.com/characters/Skin/12/Lillia.png",
            "price": 1,
        },
        "Nomsy": {
            "url": "https://rerollcdn.com/characters/Skin/12/Nomsy.png",
            "price": 1,
        },
        "Poppy": {
            "url": "https://rerollcdn.com/characters/Skin/12/Poppy.png",
            "price": 1,
        },
        "Seraphine": {
            "url": "https://rerollcdn.com/characters/Skin/12/Seraphine.png",
            "price": 1,
        },
        "Soraka": {
            "url": "https://rerollcdn.com/characters/Skin/12/Soraka.png",
            "price": 1,
        },
        "Twitch": {
            "url": "https://rerollcdn.com/characters/Skin/12/Twitch.png",
            "price": 1,
        },
        "Warwick": {
            "url": "https://rerollcdn.com/characters/Skin/12/Warwick.png",
            "price": 1,
        },
        "Ziggs": {
            "url": "https://rerollcdn.com/characters/Skin/12/Ziggs.png",
            "price": 1,
        },
        "Zoe": {"url": "https://rerollcdn.com/characters/Skin/12/Zoe.png", "price": 1},
        "Ahri": {
            "url": "https://rerollcdn.com/characters/Skin/12/Ahri.png",
            "price": 2,
        },
        "Akali": {
            "url": "https://rerollcdn.com/characters/Skin/12/Akali.png",
            "price": 2,
        },
        "Cassiopeia": {
            "url": "https://rerollcdn.com/characters/Skin/12/Cassiopeia.png",
            "price": 2,
        },
        "Galio": {
            "url": "https://rerollcdn.com/characters/Skin/12/Galio.png",
            "price": 2,
        },
        "Kassadin": {
            "url": "https://rerollcdn.com/characters/Skin/12/Kassadin.png",
            "price": 2,
        },
        "KogMaw": {
            "url": "https://rerollcdn.com/characters/Skin/12/KogMaw.png",
            "price": 2,
        },
        "Nilah": {
            "url": "https://rerollcdn.com/characters/Skin/12/Nilah.png",
            "price": 2,
        },
        "Nunu": {
            "url": "https://rerollcdn.com/characters/Skin/12/Nunu.png",
            "price": 2,
        },
        "Rumble": {
            "url": "https://rerollcdn.com/characters/Skin/12/Rumble.png",
            "price": 2,
        },
        "Shyvana": {
            "url": "https://rerollcdn.com/characters/Skin/12/Shyvana.png",
            "price": 2,
        },
        "Syndra": {
            "url": "https://rerollcdn.com/characters/Skin/12/Syndra.png",
            "price": 2,
        },
        "Tristana": {
            "url": "https://rerollcdn.com/characters/Skin/12/Tristana.png",
            "price": 2,
        },
        "Zilean": {
            "url": "https://rerollcdn.com/characters/Skin/12/Zilean.png",
            "price": 2,
        },
        "Bard": {
            "url": "https://rerollcdn.com/characters/Skin/12/Bard.png",
            "price": 3,
        },
        "Ezreal": {
            "url": "https://rerollcdn.com/characters/Skin/12/Ezreal.png",
            "price": 3,
        },
        "Hecarim": {
            "url": "https://rerollcdn.com/characters/Skin/12/Hecarim.png",
            "price": 3,
        },
        "Hwei": {
            "url": "https://rerollcdn.com/characters/Skin/12/Hwei.png",
            "price": 3,
        },
        "Jinx": {
            "url": "https://rerollcdn.com/characters/Skin/12/Jinx.png",
            "price": 3,
        },
        "Katarina": {
            "url": "https://rerollcdn.com/characters/Skin/12/Katarina.png",
            "price": 3,
        },
        "Mordekaiser": {
            "url": "https://rerollcdn.com/characters/Skin/12/Mordekaiser.png",
            "price": 3,
        },
        "Neeko": {
            "url": "https://rerollcdn.com/characters/Skin/12/Neeko.png",
            "price": 3,
        },
        "Shen": {
            "url": "https://rerollcdn.com/characters/Skin/12/Shen.png",
            "price": 3,
        },
        "Swain": {
            "url": "https://rerollcdn.com/characters/Skin/12/Swain.png",
            "price": 3,
        },
        "Veigar": {
            "url": "https://rerollcdn.com/characters/Skin/12/Veigar.png",
            "price": 3,
        },
        "Vex": {"url": "https://rerollcdn.com/characters/Skin/12/Vex.png", "price": 3},
        "Wukong": {
            "url": "https://rerollcdn.com/characters/Skin/12/Wukong.png",
            "price": 3,
        },
        "Fiora": {
            "url": "https://rerollcdn.com/characters/Skin/12/Fiora.png",
            "price": 4,
        },
        "Gwen": {
            "url": "https://rerollcdn.com/characters/Skin/12/Gwen.png",
            "price": 4,
        },
        "Kalista": {
            "url": "https://rerollcdn.com/characters/Skin/12/Kalista.png",
            "price": 4,
        },
        "Karma": {
            "url": "https://rerollcdn.com/characters/Skin/12/Karma.png",
            "price": 4,
        },
        "Nami": {
            "url": "https://rerollcdn.com/characters/Skin/12/Nami.png",
            "price": 4,
        },
        "Nasus": {
            "url": "https://rerollcdn.com/characters/Skin/12/Nasus.png",
            "price": 4,
        },
        "Olaf": {
            "url": "https://rerollcdn.com/characters/Skin/12/Olaf.png",
            "price": 4,
        },
        "Rakan": {
            "url": "https://rerollcdn.com/characters/Skin/12/Rakan.png",
            "price": 4,
        },
        "Ryze": {
            "url": "https://rerollcdn.com/characters/Skin/12/Ryze.png",
            "price": 4,
        },
        "TahmKench": {
            "url": "https://rerollcdn.com/characters/Skin/12/TahmKench.png",
            "price": 4,
        },
        "Taric": {
            "url": "https://rerollcdn.com/characters/Skin/12/Taric.png",
            "price": 4,
        },
        "Varus": {
            "url": "https://rerollcdn.com/characters/Skin/12/Varus.png",
            "price": 4,
        },
        "Briar": {
            "url": "https://rerollcdn.com/characters/Skin/12/Briar.png",
            "price": 5,
        },
        "Camille": {
            "url": "https://rerollcdn.com/characters/Skin/12/Camille.png",
            "price": 5,
        },
        "Diana": {
            "url": "https://rerollcdn.com/characters/Skin/12/Diana.png",
            "price": 5,
        },
        "Milio": {
            "url": "https://rerollcdn.com/characters/Skin/12/Milio.png",
            "price": 5,
        },
        "Morgana": {
            "url": "https://rerollcdn.com/characters/Skin/12/Morgana.png",
            "price": 5,
        },
        "Norra": {
            "url": "https://cdn.metatft.com/cdn-cgi/image/width=48,height=48,format=auto/https://cdn.metatft.com/file/metatft/champions/tft12_norra.png",
            "price": 5,
        },
        "Smolder": {
            "url": "https://rerollcdn.com/characters/Skin/12/Smolder.png",
            "price": 5,
        },
        "Xerath": {
            "url": "https://rerollcdn.com/characters/Skin/12/Xerath.png",
            "price": 5,
        },
    }

    # Champion list setup based on units in latest_match
    champions = []
    unit_data = latest_match["summary"]["units"]

    for unit in unit_data:
        character_name = unit["character_id"].replace("TFT12_", "")
        unit_tier = unit.get("tier", 0)  # Extract the tier for each unit
        if character_name in champion_assets:
            champion_info = champion_assets[character_name]
            champions.append(
                {
                    "icon": champion_info["url"],
                    "stars": "★" * int(unit_tier),
                    "price": champion_info["price"],
                }
            )

    # HTML template for the match summary
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=League+Spartan:wght@100..900&display=swap" rel="stylesheet">
    <style>
        @font-face {
            font-family: 'CustomFont1';
            src: url('fonts/CustomFont1-Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        @font-face {
            font-family: 'CustomFont2';
            src: url('fonts/CustomFont2-Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        * {
            box-sizing: border-box;
        }
        body {
            font-family: 'CustomFont1', 'League Spartan', sans-serif;
            background-color: #242944;
            color: #f7f7f7;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            padding: 20px;
            background-color: #2c2f33;
            max-width: 1000px;
            border-radius: 9px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .meme-image {
            flex-shrink: 0;
            margin-right: 15px;
            width: 180px;

            height: 210px;

            overflow: hidden;
            border-radius: 7px;
            background-color: transparent;
        }

        .meme-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
            display: block;
        }
        .content {
            display: flex;
            flex-direction: column;
            gap: 15px;
            width: 100%;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            width: 100%;
        }
        .stats {
            flex: 1;
            font-size: 18px;
            color: #f7f7f7;
        }
        .ranked-info {
            font-size: 18px;
            margin-bottom: 5px;
            color: #f7f7f7;
        }
        .time-info {
            font-size: 18px;
            margin-bottom: 5px;
            color: #f7f7f7;
        }
        .lp-info {
            font-size: 20px;
            margin-top: 12px;
            margin-bottom: 5px;
            color: #f7f7f7;
        }
        .rank-rating-label {
            color: #cc583f; /* Bright green color for the rank rating label */
            font-weight: bold;
        }
        .time-label {
            color: #f7f7f7; 
            font-weight: bold;
        }
        .lp-label {
            color: #f7f7f7; 
            font-weight: bold;
        }
        .highlight {
            font-size: 36px;
            font-weight: bold;
            color: #ff6347;
        }
        
        .username-tag {
            display: flex;
            align-items: center;
            text-align: left;
            font-size: 24px;
            color: #f7f7f7;
        }
        .summoner-icon {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            overflow: hidden;
            margin-right: 10px;
            display: inline-block;
            background-color: #ccc;
        }
        .summoner-icon img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
        .username-info {
            display: flex;
            flex-direction: column; 
        }
        .username {
            font-weight: bold;
        }
        .placement {
            font-size: 58px;
            color: #ffd700;
            font-weight: bold;
            margin-top: 5px;
        }
        .champion-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: flex-start;
            padding-top: 0px;
        }
        .champion-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            width:45px;
        }
        .champion-icon {
            width: 45px;
            height: 45px;
            border-radius: 7px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        .augment-list {
            display: flex;
            flex-wrap: wrap;
            gap: 2px;
        }
        .augment-icon {
            border-radius: 50%;
            width: 36px;
            height: 36px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        .price-1 {
            border: 2.5px solid #ffffff; /* White */
        }

        .price-2 {
            border: 2.5px solid #00ff00; /* Green */
        }

        .price-3 {
            border: 2.5px solid #0000ff; /* Blue */
        }

        .price-4 {
            border: 2.5px solid #800080; /* Purple */
        }

        .price-5 {
            border: 2.5px solid #ffd700; /* Gold */
        }
        .champion-icon img {
            width: 100%;
            height: 100%;
            border-radius: 8px;
            object-fit: cover;
        }
        .champion-stars {
            color: #ffd700; /* Gold color for stars */
            font-size: 18px;
        }
        
        /* Responsive adjustments for champion-item */
        @media (max-width: 768px) {
            .champion-item {
                width: 50px;
            }
            .champion-icon {
                width: 50px;
                height: 50px;
            }
            .champion-stars {
                font-size: 14px;
            }
        }
        
        @media (max-width: 480px) {
            .champion-item {
                width: 40px;
            }
            .champion-icon {
                width: 40px;
                height: 40px;
            }
            .champion-stars {
                font-size: 12px;
            }
        }
        strong {
            color: #00ff00; /* Bright green color for strong elements */
        }
        .placement-gold-1 {
            border: 2px solid #ffd700; /* Bright Gold */
            
        }

        .placement-gold-2 {
            border: 2px solid #e6c200; /* Slightly Darker Gold */
            
        }

        .placement-gold-3 {
            border: 2px solid #ccac00; /* Even Darker Gold */
            
        }

        .placement-gold-4 {
            border: 2px solid #b39700; /* Darkest Gold */
            
        }

        .placement-gray {
            border: 2px solid #808080; /* Gray */
            
        }
        .bg-gold-1 {
            background-color: #ffd700;
            
        }

        .bg-gold-2 {
            background-color: #e6c200;
            
        }

        .bg-gold-3 {
            background-color: #ccac00;
            
        }

        .bg-gold-4 {
            background-color: #b39700;
            
        }

        .bg-gray {
            background-color: #808080;
            
        }
    </style>
</head>
<body class="{{ color_bg }}">
    <div class="container {{ color_class }}">
        <div class="meme-image">
            <img src="{{ meme_image }}" alt="Meme Image">
        </div>

        <div class="content">
            <div class="header">
                <div class="stats">
                    <div class="ranked-info">
                        <span class="rank-rating-label">Rank:</span> 
                        <img src="{{ stats.rank_icon }}" alt="Rank Icon" style="width: 20px; height: 20px; vertical-align: middle;">
                        <span style="color: {{ stats.rank_color }};">{{ stats.rank }}</span> 
                        <span style="color: #f7f7f7;">{{ stats.rank_roman }}</span>
                    </div>
                    <div class="time-info">
                        <span class="time-label">Time:</span> {{ stats.time }}
                    </div>
                    <div class="time-info">
                        <span class="time-label">Match Duration:</span> {{ stats.duration }}
                    </div>
                    <div class="lp-info">
                        <span class="lp-label">LP:</span> <span class="highlight" style="color: {{ stats.lp_change_color }};">{{ stats.lp_change }}</span>
                    </div>
                </div>

                <div class="username-tag">
                    <div class="summoner-icon">
                        <img src="{{ tacticians_icon_url }}" alt="Summoner Icon" onerror="this.onerror=null; this.src='https://via.placeholder.com/50';">
                    </div>
                    <div class="username-info">
                        <div class="username">
                            {{ summoner_name }}#{{ tag }}
                        </div>
                        <div class="placement">
                            {{ placement }}{{ ordinal }}
                        </div>
                        <div class="augment-list">
                            {% for augment in augment_urls %}
                            <img src="{{ augment }}" alt="Augment Icon" class="augment-icon">
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>

            <div class="champion-list">
                {% for champion in champions %}
                <div class="champion-item">
                    <div class="champion-icon price-{{ champion.price }}">
                        <img src="{{ champion.icon }}" alt="Champion Icon" onerror="this.onerror=null; this.src='https://via.placeholder.com/50';">
                    </div>
                    <div class="champion-stars">{{ champion.stars }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>

"""

    # Modify the data rendering logic to include the ordinal suffix
    def get_ordinal_suffix(number):
        if 10 <= number % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
        return suffix

    def get_border_class_by_placement(placement):
        if 1 <= placement <= 4:
            return f"placement-gold-{placement}"
        else:
            return "placement-gray"

    def get_bg_color_by_placement(placement):
        if 1 <= placement <= 4:
            return f"bg-gold-{placement}"
        else:
            return "bg-gray"

    # Generate the ordinal suffix for the placement
    placement = latest_match["placement"]
    ordinal_suffix = get_ordinal_suffix(placement)

    # Determine the border class based on placement
    border_class = get_border_class_by_placement(placement)
    bg_color = get_bg_color_by_placement(placement)

    tacticians_icon_url = (
        f"https://cdn.metatft.com/file/metatft/tacticians/{tacticians_icon}.png"
    )

    # Render the HTML with Jinja2
    template = Template(html_template)
    rendered_html = template.render(
        placement=placement,
        ordinal=ordinal_suffix,
        summoner_name=summoner["riot_id"].split("#")[0],
        tag=summoner["riot_id"].split("#")[1],
        meme_image=meme_image,
        stats=stats,
        champions=champions,
        ranked=ranked,
        tacticians_icon_url=tacticians_icon_url,
        color_class=border_class,
        color_bg=bg_color,
        augment_urls=augment_urls,
    )

    # Write HTML to file and capture screenshot
    with open("match_summary.html", "w", encoding="utf-8") as file:
        file.write(rendered_html)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("file://" + os.path.abspath("match_summary.html"))
        time.sleep(1)  # Allow time to render

        # Wait for the container to load and locate it
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container"))
        )

        # Capture screenshot of the container element only
        image_name = f"match_summary_banner_{puid}.png"
        screenshot_path = image_name
        container.screenshot(screenshot_path)
        print(f"Saved banner to {screenshot_path}")
        return image_name
    finally:
        driver.quit()
        os.remove("match_summary.html")


def show_match_detail(profile_data, folder_path="."):
    # Extract player stats and traits from `profile_data`
    match_summary = profile_data["matches"][0]["summary"]
    player_data = {
        "level": match_summary.get("level", "N/A"),
        "time_eliminated": match_summary.get("time_eliminated", "N/A"),
        "last_round": match_summary.get("last_round", "N/A"),
        "total_damage_to_players": match_summary.get("total_damage_to_players", "N/A"),
        "players_eliminated": match_summary.get("players_eliminated", "N/A"),
        "player_rating": match_summary.get("player_rating", "N/A"),
        "player_rating_numeric": match_summary.get("player_rating_numeric", "N/A"),
        "traits": ", ".join(match_summary.get("traits", [])),
    }

    # HTML template as a string
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @font-face {
                font-family: 'CustomFont1';
                src: url('fonts/CustomFont1-Regular.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            @font-face {
                font-family: 'CustomFont2';
                src: url('fonts/CustomFont2-Regular.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            body { 
                font-family: 'CustomFont1', Arial, sans-serif; 
                background-color: #2c2f33; 
                color: #f7f7f7; 
            }
            .container { width: 400px; padding: 20px; background-color: #23272a; border-radius: 8px; margin: auto; }
            .header { font-size: 24px; font-weight: bold; margin-bottom: 15px; text-align: center; }
            .stats { font-size: 16px; line-height: 1.6; }
            .traits { font-size: 14px; color: #b9bbbe; margin-top: 10px; }
            .stat-item { margin-bottom: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Player Stats</div>
            <div class="stats">
                <div class="stat-item">Level: {{ level }}</div>
                <div class="stat-item">Time Eliminated: {{ time_eliminated }} seconds</div>
                <div class="stat-item">Last Round: {{ last_round }}</div>
                <div class="stat-item">Total Damage to Players: {{ total_damage_to_players }}</div>
                <div class="stat-item">Players Eliminated: {{ players_eliminated }}</div>
                <div class="stat-item">Rating: {{ player_rating }} ({{ player_rating_numeric }})</div>
            </div>
            <div class="traits">
                <strong>Traits:</strong> {{ traits }}
            </div>
        </div>
    </body>
    </html>
    """

    # Render the HTML with Jinja2
    template = Template(html_template)
    rendered_html = template.render(**player_data)

    # Save the rendered HTML to a temporary file
    html_file_path = os.path.join(folder_path, "match_detail.html")
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    # Set up Selenium for headless operation
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open the HTML file in Selenium
        driver.get("file://" + os.path.abspath(html_file_path))
        time.sleep(1)  # Wait for the page to fully render

        # Capture screenshot using the updated method
        screenshot_path = os.path.join(folder_path, "match_detail.png")
        element = driver.find_element(By.TAG_NAME, "body")  # Capture the whole page
        element.screenshot(screenshot_path)  # Save screenshot as a PNG file
        print(f"Player stats image saved to {screenshot_path}")

        return screenshot_path  # Return path to the screenshot
    finally:
        driver.quit()
        os.remove(html_file_path)


def get_latest_match_data(profile_data):
    """Fetches the match data URL for the latest match."""
    # Safely access 'app_matches' and check if it contains any data
    app_matches = profile_data.get("app_matches", {})
    # print(app_matches)
    if not app_matches:
        print("No matches available in 'app_matches'.")
        return None

    # Sort app_matches by 'created_timestamp' in descending order to get the latest match first
    sorted_matches = sorted(
        app_matches, key=lambda x: x["created_timestamp"], reverse=True
    )
    latest_match_url = sorted_matches[0].get("match_data_url")

    if latest_match_url:
        # print(f"Latest match URL: {latest_match_url}")
        return latest_match_url
    else:
        print("No match_data_url found in the latest match.")
        return None


def match_data_convert(url):
    """Fetches and cleans up JSON data from the given URL."""
    response = requests.get(url)
    data = response.json()

    # Check if 'stage_data' is a string and try to decode it if necessary
    if "stage_data" in data and isinstance(data["stage_data"], str):
        try:
            # First, attempt to load 'stage_data' as JSON if it's a string
            data["stage_data"] = json.loads(data["stage_data"])
        except json.JSONDecodeError:
            print("Failed to parse 'stage_data' JSON. Attempting cleanup.")
            # If parsing fails, proceed with escape character replacements
            data["stage_data"] = (
                data["stage_data"]
                .replace('\\\\\\"', '"')
                .replace('\\\\"', '"')
                .replace('\\"', '"')
            )
            data["stage_data"] = (
                data["stage_data"]
                .replace('"[', "[")
                .replace(']"', "]")
                .replace('"{', "{")
                .replace('}"', "}")
            )
            try:
                # Try loading as JSON again after cleanup
                data["stage_data"] = json.loads(data["stage_data"])

            except json.JSONDecodeError:
                print("Failed to clean and parse 'stage_data'. Setting as empty list.")
                data["stage_data"] = []  # Set as empty list if parsing fails
    data = organize_stage_data(data)
    # Save the cleaned data to a JSON file
    with open("cleaned_match_data.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)
        print("Cleaned match data saved to cleaned_match_data.json")

    return data

def generate_match_rounds_report(riot_id, tag, profile_data, folder_path="."):
    rounds = []
    total_rerolls = 0
    total_gold_spent = 0
    total_damage_dealt = 0
    total_repositions = 0
    total_gold_earned = 0
    apm_list = []
    final_rank = None
    previous_gold = None
    victories = 0
    defeats = 0

    # Fetch the latest match data URL for the given riot_id and tag
    latest_match_data_url = get_latest_match_data(profile_data)
    if not latest_match_data_url:
        print("No match data URL found.")
        return None

    # Fetch and parse match data JSON from the URL
    match_data = match_data_convert(latest_match_data_url)

    # Process each stage in match data to collect round information
    for stage_key, stage_data in match_data.items():
        player_data = stage_data.get("me", {})

        # Check if the player's summoner name matches the specified riot_id
        if player_data.get("summoner_name") != riot_id:
            continue

        # Extract health and handle potential issues with data types
        health_str = player_data.get("health", "N/A")
        try:
            health = int(health_str)
        except ValueError:
            health = "N/A"

        # Extract rerolls and ensure it's an integer
        rerolls = stage_data.get("rerolls", 0)
        try:
            rerolls = int(rerolls)
        except (ValueError, TypeError):
            rerolls = 0

        # Extract current gold and handle empty strings or missing values
        current_gold_str = player_data.get("gold", "0")
        try:
            current_gold = int(current_gold_str)
        except (ValueError, TypeError):
            current_gold = 0

        # Calculate gold spent for this round
        if previous_gold is None:
            gold_spent = 0  # First stage, no previous gold to compare
        else:
            gold_spent = max(previous_gold - current_gold, 0)  # Ensure gold_spent is non-negative

        # Accumulate total rerolls and gold spent
        total_rerolls += rerolls
        total_gold_spent += gold_spent
        previous_gold = current_gold  # Update previous gold for the next iteration

        # Accumulate total damage dealt
        # local_player_damage = stage_data.get("local_player_damage", {})
        # units_damage = local_player_damage.get("units", {})
        # round_damage = 0

        # for unit in units_damage.values():
        #     unit_damage = unit.get("damage") or 0  # Ensure unit_damage is a number
        #     round_damage += unit_damage

        # total_damage_dealt += round_damage

        # Accumulate total repositions
        repositions = stage_data.get("repositions", 0)
        try:
            repositions = int(repositions)
        except (ValueError, TypeError):
            repositions = 0
        total_repositions += repositions

        # Accumulate total gold earned
        gold_earned = stage_data.get("gold_earned", 0)
        try:
            gold_earned = int(gold_earned)
        except (ValueError, TypeError):
            gold_earned = 0
        total_gold_earned += gold_earned

        # Accumulate APM
        actions = stage_data.get("actions", {})
        apm_stage = actions.get("apm", 0)
        try:
            apm_stage = int(apm_stage)
        except (ValueError, TypeError):
            apm_stage = 0
        if apm_stage > 0:
            apm_list.append(apm_stage)

        # Determine round outcome and color
        round_outcome = stage_data.get("match_info", {}).get("round_outcome", {})
        # Find the correct key in round_outcome that matches riot_id or tag_line
        outcome = None
        for player_name, info in round_outcome.items():
            if player_name == riot_id or info.get('tag_line') == tag:
                outcome = info.get('outcome', 'N/A')
                break
        if outcome is None:
            outcome = 'N/A'

        tile_color = "victory" if outcome == "victory" else "defeat"

        # Count victories and defeats
        if outcome == "victory":
            victories += 1
        elif outcome == "defeat":
            defeats += 1

        # Get player's rank from the last stage
        rank = player_data.get("rank")
        if rank is not None:
            final_rank = rank

        # Prepare round data, including the stage number (e.g., '1-2')
        round_data = {
            "stage_number": stage_key,  # Add the stage key here
            "result": outcome,
            "health": health,
            "rerolls": rerolls,
            "gold_spent": gold_spent,  # Gold spent in this round
            "color": tile_color,
        }
        rounds.append(round_data)

    # Sort the rounds by stage_number
    def parse_stage_number(stage):
        try:
            parts = stage.split('-')
            return int(parts[0]), int(parts[1])
        except:
            return (0, 0)

    rounds.sort(key=lambda x: parse_stage_number(x['stage_number']))

    # Calculate average APM
    if apm_list:
        average_apm = sum(apm_list) / len(apm_list)
        average_apm = round(average_apm, 2)
    else:
        average_apm = "N/A"

    # Calculate Win Rate
    total_games = victories + defeats
    if total_games > 0:
        win_rate = (victories / total_games) * 100
        win_rate = round(win_rate, 2)
    else:
        win_rate = "N/A"

    # Generate Overall Score
    def generate_overall_score(total_rerolls, total_gold_spent, average_apm, final_rank, win_rate, total_damage_dealt):
        messages = []

        # Rerolls Messages
        if total_rerolls > 50:
            reroll_msgs = [
                "Rollin' like a DJ! Maybe save some gold next time.",
                "Did you think the shop was a slot machine?",
                "High roller alert! Casinos would be jealous.",
                "You rerolled more than a hamster on a wheel!",
                "Is 'R' your favorite key? Consider an intervention.",
                "Your rerolls are the real MVP of this game.",
                "You’re the reason rerolling was invented.",
                "You should get a sponsorship from the RNG gods.",
                "You re-rolled so much it’s practically a lifestyle choice!",
                "Gold wasted, but your excitement is palpable!"
            ]
        else:
            reroll_msgs = [
                "Efficient rolling! Your economy thanks you.",
                "Gold saver! You could teach Scrooge McDuck.",
                "Rolling minimally like a true strategist.",
                "Nice restraint on the rerolls!",
                "Your patience is commendable. Well done!",
                "You saved more gold than the entire server combined!",
                "You know what they say: patience is a virtue... and a gold saver.",
                "Low rerolls, high IQ. Well played.",
                "Efficiency at its finest. Who needs luck when you've got skill?",
                "If only your rerolls were as effective as your planning!"
            ]
        messages.append(random.choice(reroll_msgs))

        # APM Messages
        if average_apm != "N/A" and average_apm < 20:
            apm_msgs = [
                "APM lower than a sloth's heartbeat. Wake up!",
                "Did you fall asleep on the keyboard?",
                "Your APM suggests you're playing with your feet.",
                "Even a snail moves faster than that.",
                "At this rate, glaciers are melting faster than you move.",
                "Did you mistake this for a chill game of Solitaire?",
                "Your APM is so slow, even dial-up internet is jealous.",
                "Bro, are you playing on a toaster?",
                "Maybe try hitting the buttons harder? That usually helps.",
                "Your APM is giving slow motion a run for its money."
            ]
        else:
            apm_msgs = [
                "Swift hands! You're on fire.",
                "Your APM is over 9000! Well, almost.",
                "Fingers moving faster than a caffeinated squirrel!",
                "Are you part robot? Impressive speed!",
                "Blazing fast! Do you even blink?",
                "Your APM's so fast, the game can't even keep up.",
                "The Flash could take notes from your fingers.",
                "You're practically on turbo mode. Slow down!",
                "More APM than a competitive eSports player. Respect.",
                "Is there a keyboard shortcut for 'legendary'?"
            ]
        messages.append(random.choice(apm_msgs))

        # Final Rank Messages
        if final_rank is not None:
            if int(final_rank) == 1:
                rank_msgs = [
                    "Champion! You're the TFT master!",
                    "First place! Did you write the game's code?",
                    "Unstoppable! Everyone else was just a spectator.",
                    "You came, you saw, you conquered!",
                    "Victory Royale! Oops, wrong game, but you get it.",
                    "World’s best player? Yep, that’s you.",
                    "You’re so good, they should rename the game after you.",
                    "Top tier performance, like you’ve been practicing since birth.",
                    "All hail the king of the leaderboard!",
                    "No one else stood a chance. You were a one-man army."
                ]
            elif int(final_rank) > 4:
                rank_msgs = [
                    "Better luck next time. Aim for top 4!",
                    "At least you had fun, right?",
                    "The bottom half needs love too!",
                    "Someone has to be in the lower ranks; thanks for volunteering.",
                    "Looks like you took the scenic route to defeat.",
                    "You’re like the support role of this match: invaluable, but not at the top.",
                    "More practice, and maybe next time you’ll get closer to that sweet, sweet top 4.",
                    "The bottom was waiting for you, and you didn’t disappoint.",
                    "Well, at least you weren’t last! There's that.",
                    "Don’t worry, we all start somewhere, but where you ended up... yeah, it’s a start."
                ]
            else:
                rank_msgs = [
                    "Great job reaching top 4!",
                    "Solid performance! Almost there.",
                    "So close to the top! Keep pushing.",
                    "You're in the upper echelon! Well played.",
                    "Impressive! You're a force to be reckoned with.",
                    "Top 4, baby! You’re practically famous.",
                    "You didn’t win, but you sure made it look good.",
                    "Better than most, but not quite there yet.",
                    "Top 4 is where the real magic happens. Keep up the grind.",
                    "Solid performance, but your throne is still waiting."
                ]
        else:
            rank_msgs = [
                "Rank unavailable. Did you even play?",
                "We can't find your rank; are you a ghost?",
                "Invisible player detected! Spooky.",
                "No rank data. Did you rage quit?",
                "Lost in the void of unranked games.",
                "Trying to rank up, or just hiding in plain sight?",
                "Where are you? Your rank is playing hide-and-seek.",
                "No rank? Maybe try not AFKing next time?",
                "Did you get lost on your way to ranking?",
                "Your rank is still under construction."
            ]
        messages.append(random.choice(rank_msgs))

        # Win Rate Messages
        if win_rate != "N/A":
            if win_rate > 50:
                winrate_msgs = [
                    "Winning more than losing. Keep it up!",
                    "Victory tastes sweet, doesn't it?",
                    "You're on a roll! Keep the wins coming.",
                    "Winning streak! Your enemies tremble.",
                    "GG EZ. Am I right?",
                    "Winning like it's your full-time job.",
                    "You have a higher win rate than my hopes and dreams.",
                    "Look at you, climbing that win ladder!",
                    "You're living the dream. Keep winning!",
                    "The victory train has no brakes with you at the wheel."
                ]
            else:
                winrate_msgs = [
                    "Losing streak? Time to rethink your strategy.",
                    "Wins are overrated anyway, right?",
                    "Practice makes perfect. Keep trying!",
                    "You miss 100% of the shots you don't take... and some you do.",
                    "Maybe let the cat play next time?",
                    "It’s not losing, it’s ‘preparing for future victories.’",
                    "You can’t win ‘em all, but you sure tried!",
                    "Looks like you’re building character... slowly.",
                    "Every loss is a lesson... but you’ve got a lot of lessons.",
                    "Your win rate is currently in 'hero's journey' mode."
                ]
            messages.append(random.choice(winrate_msgs))

        # Total Damage Messages
        if total_damage_dealt > 1000000:
            damage_msgs = [
                "You didn’t just deal damage; you obliterated them.",
                "That’s not damage, that’s an act of war.",
                "Are you sure you're not playing with a nuke?",
                "Your damage numbers are a thing of legends.",
                "Damage dealer? More like damage king.",
                "That’s not damage, that’s devastation.",
                "You hit harder than a meteor falling from the sky.",
                "Your damage numbers could give someone PTSD.",
                "Did you make the enemy team cry? Because they should."
            ]
        else:
            damage_msgs = [
                "Damage is damage. We’ll get ‘em next time.",
                "It’s a start... let’s aim for more next time!",
                "Could be more, could be less, but it’s damage.",
                "You’ve got potential, just a little more oomph.",
                "At least the enemy knows you’re there now.",
                "You made a dent, not a crater. Yet.",
                "Well, you didn’t let them walk all over you, that’s progress.",
                "Every point of damage is a step toward domination!",
                "Next time, hit ‘em harder. You got this."
            ]
        messages.append(random.choice(damage_msgs))

        # Combine messages into overall_score
        overall_score = " ".join(messages)
        return overall_score


    overall_score = generate_overall_score(total_rerolls, total_gold_spent, average_apm, final_rank, win_rate, total_damage_dealt)
    # formatted_total_damage_dealt = "{:,}".format(total_damage_dealt)
    # HTML template for displaying per-round and total gold spent
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
        <title>Match Rounds</title>
        <style>
            body {
                font-family: "Noto Sans", serif;
                font-optical-sizing: auto;
                font-style: normal;
                background-color: #242944;
                color: #f7f7f7;
                display: flex;
                justify-content: start;
                align-items: flex-start;
                height: 100vh;
                padding: 20px;
                margin: 0;
            }
            .container {
                padding: 20px;
                background-color: #2c2f33;
                max-width: 786px;
                position: relative;
                justify-content: start;
            }
            .summary-container {
                display: flex;
                position: absolute;
                top: 20px;
                left: 20px;
                min-height: 150px;
                max-height: 150px;
                width: 100%;  
            }

            .summary {
                font-size: 14px;
                margin-right: 10px;
                border: 2px solid #ffffff;
                min-width: 170px;
                max-width: 230px;
                border-radius: 5px;
                padding: 8px;
                background-color: #3f4247;
                flex-grow: 0;  
                width: auto; 
            }

            /* Add a new class for the third summary to fill the space */
            .summary-third {
                font-size: 13px;
                border: 2px solid #ffffff;
                max-width: 370px;
                border-radius: 5px;
                padding: 8px;
                background-color: #3f4247;
                flex-grow: 1;  /* This will make it stretch to fill the remaining space */
                width: auto;
            }
            .summary strong {
                color: #FFFFFF; /* Bright white for contrast */
                font-size: 16px; /* Increase font size */
                display: block; /* Ensure it takes full width */
                margin-bottom: 3px; /* Add some spacing */
            }
            .summary-third strong {
                font-size: 16px; /* Slightly smaller font size */
                display: block; /* Ensure it takes full width */
                margin-bottom: 3px; /* Add some spacing */
            }
            .rounds-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: start;
                margin-top: 160px;
                border: 2px solid #ffffff;
                background-color: #37436d;
                border-radius: 5px;
                padding: 15px;
            }
            .rounds-container-name{
                display: flex;
                font-size: 16px;
                font-weight: 500;
                width: 100%;
                position: relative;
                margin-bottom: 5px;
                
            }
            .round-tile {
                width: 30px;
                height: 110px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                border-radius: 4px;
                border: 2.5px solid #ffffff;
                color: #ffffff;
                padding: 6px;
                margin: 2px;
            }
            .round-tile.victory { background-color: #4CAF50; }
            .round-tile.defeat { background-color: #F44336; }
            .stage-container {
                text-align: center;
                margin-bottom: 10px;
            }
            .overall-score-text {
                color: #FFD700; /* Bright yellow color */
                font-style: italic; /* Optional: make the text italic */
                font-weight: bold; /* Optional: make the text bold */
            }
            .stage-number {
                font-size: 14px;
                font-weight: bold;
            }
            .stage-title {
                font-size: 8px;
                font-weight: normal;
                margin-bottom: 0px;
            }
            .result-text {
                font-size: 21px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .round-info {
                font-size: 11px;
                text-align: center;
                line-height: 1.6;
            }
            .info-item {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            .gold-icon {
                margin-left: 2px;
            }
            .reroll-icon {
                align-self: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="summary-container">
                <div class="summary">
                    <strong>💰 Economy 💰</strong>
                    Total Gold Spent : {{ total_gold_spent }}<br>
                    Total Rerolls Spent : {{ total_rerolls }}<br>
                    ECO Rank : {{ eco_rank }}
                </div>
                <div class="summary">
                    <strong>🔥 Performance 🔥</strong>
                    Total Repositions : {{ total_repositions }}<br>
                    Average APM : {{ average_apm }}<br>
                    Win Rate : {{ win_rate }}%<br>
                    Final Rank : {{ final_rank }}
                </div>
                <div class="summary-third">
                    <strong>🏆 Game Summary 🏆</strong>
                    <span class="overall-score-text">{{ overall_score }}<br>{{ some_cool_funny_text }}</span>
                </div>
            </div>
            <div class="rounds-container">
                <div class="rounds-container-name">Rounds 👉👇</div>
                {% for round in rounds %}
                <div class="round-tile {{ round.color }}">
                    <div class="stage-container">
                        <div class="stage-title">Round</div>
                        <div class="stage-number">{{ round.stage_number }}</div>
                    </div>
                    <div class="result-text">
                        {% if round.result == "victory" %}W{% else %}L{% endif %}
                    </div>
                    <div class="round-info">
                        <div class="info-item">
                            <img src="{{ gold_icon_url }}" alt="Gold Icon" class="gold-icon" style="width: 12px;">
                            {{ round.gold_spent }}
                        </div>
                        <div class="info-item">
                            <img src="{{ reroll_icon_url }}" alt="Reroll Icon" class="reroll-icon" style="width: 16px;">
                            {{ round.rerolls }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """

    # Icon URLs and rendering setup
    reroll_icon_url = "https://www.metatft.com/icons/reroll_default.png"
    gold_icon_url = "https://www.metatft.com/icons/gold2.png"
    eco_rank = "A"  # Placeholder for ECO rank if applicable

    template = Template(html_template)
    rendered_html = template.render(
        total_rerolls=total_rerolls,
        total_gold_spent=total_gold_spent,
        # formatted_total_damage_dealt=formatted_total_damage_dealt,
        total_repositions=total_repositions,
        average_apm=average_apm,
        final_rank=final_rank if final_rank is not None else "N/A",
        win_rate=win_rate,
        overall_score=overall_score,
        rounds=rounds,
        reroll_icon_url=reroll_icon_url,
        gold_icon_url=gold_icon_url,
        eco_rank=eco_rank
    )

    # Save and capture the HTML as an image
    html_file_path = os.path.join(folder_path, "match_rounds_compact.html")
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("file://" + os.path.abspath(html_file_path))
        time.sleep(1)
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container"))
        )
        screenshot_path = os.path.join(folder_path, "match_rounds_compact.png")
        container.screenshot(screenshot_path)
        
        print(f"Compact match rounds image saved to {screenshot_path}")

        return screenshot_path
    finally:
        driver.quit()
        os.remove(html_file_path)


def load_percentile_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def show_win_rate_graph():
    # Ensure the directory and file pattern
    directory = "outputs"  # Ensure this path exists
    pattern = "tft_percentiles.json"
    json_files = glob.glob(os.path.join(directory, pattern))

    if not json_files:
        raise FileNotFoundError(
            f"No files matching the pattern {pattern} found in directory {directory}"
        )

    # Load JSON data
    json_file = json_files[0]
    data = load_percentile_data(json_file)

    # Extract stages and win rates
    stages = list(
        range(1, len(json.loads(data["percentiles"][0]["board_strength"])) + 1)
    )
    win_rates = []

    for percentile in data["percentiles"]:
        board_strength = json.loads(percentile["board_strength"])
        if len(board_strength) == len(stages):
            win_rates.append(board_strength[0])

    # Adjust lengths if necessary
    if len(win_rates) < len(stages):
        stages = stages[: len(win_rates)]
    elif len(win_rates) > len(stages):
        win_rates = win_rates[: len(stages)]

    if len(stages) != len(win_rates):
        raise ValueError(
            f"stages and win_rates must have the same length, but have shapes {len(stages)} and {len(win_rates)}"
        )

    # Plotting
    plt.figure()
    plt.plot(stages, win_rates, marker="o")
    plt.title("Win Rate per Stage")
    plt.xlabel("Stage")
    plt.ylabel("Win Rate (%)")

    # Save plot as an image file
    output_path = os.path.join(directory, "win_rate_graph.png")
    plt.savefig(output_path)
    plt.close()  # Close the plot to free memory

    return output_path  # Return the file path for Discord


if __name__ == "__main__":
    # Place any testing or standalone code here
    riot_id = "beggy"
    tag = "3105"
    profile_data = get_tft_profile(riot_id, tag)
    match_rounds_report = generate_match_rounds_report(
        riot_id, tag, profile_data, folder_path
    )
