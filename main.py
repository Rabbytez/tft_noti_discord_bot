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
import time
import re
from augments import augment_data


def get_tft_profile(riot_id, tag, tft_set="TFTSet12", include_revival_matches=True):
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
    refresh_url=f'https://api.metatft.com/public/profile/refresh_by_riotid/TH2/{riot_id}/{tag}?tier=1'
    response = requests.post(f"{refresh_url}", headers=headers)


    response = requests.get(f"{base_url}{path}", headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


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
        "color": "#6d6d6d"  # Grey for Iron
    },
    "Bronze": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/bronze.png",
        "color": "#cd7f32"  # Bronze color
    },
    "Silver": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/silver.png",
        "color": "#c0c0c0"  # Silver color
    },
    "Gold": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/gold.png",
        "color": "#ffd700"  # Gold color
    },
    "Platinum": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/platinum.png",
        "color": "#00ff00"  # Green for Platinum
    },
    "Emerald": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/emerald.png",
        "color": "#2ecc71"  # Emerald green
    },
    "Diamond": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/diamond.png",
        "color": "#00c8ff"  # Blue for Diamond
    },
    "Master": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/master.png",
        "color": "#ff00ff"  # Purple for Master
    },
    "GrandMaster": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/grandmaster.png",
        "color": "#ff4500"  # Red-orange for GrandMaster
    },
    "Challenger": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/challenger.png",
        "color": "#ff6347"  # Tomato color for Challenger
    }
}

# Function to get rank icon and color
def get_rank_icon_and_color(rating_text):
    # Split rank and tier from the rating text
    rank = rating_text.split(" ")[0]  # e.g., "EMERALD"
    rank_roman = " ".join(rating_text.split(" ")[1:])  # Join the rest of the parts
    # Get rank data if it exists, otherwise default to unranked settings
    rank_info = rank_data.get(rank.capitalize(), {"icon": "", "color": "#ffffff"})  # Default to white if rank not found
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
    puid= summoner.get("puuid", "")
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
            last_match_id_json=last_match_id

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
    print("Augment URLs:", augment_urls)

    player_rating_text = latest_match.get("summary", {}).get("player_rating_numeric", "")
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
    <title>Match Summary</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: 'League Spartan', sans-serif;
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

    tacticians_icon_url = f"https://cdn.metatft.com/file/metatft/tacticians/{tacticians_icon}.png"
    
    
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
        augment_urls=augment_urls
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
        image_name=f"match_summary_banner_{puid}.png"
        screenshot_path = image_name
        container.screenshot(screenshot_path)
        print(f"Saved banner to {screenshot_path}")
        return image_name
    finally:
        driver.quit()
        os.remove("match_summary.html")


if __name__ == "__main__":
    # Place any testing or standalone code here
    riot_id = "1010"
    tag = "ten10"
    profile_data = get_tft_profile(riot_id, tag)

    create_match_summary(profile_data)

    # create_match_summary(profile_data, True)