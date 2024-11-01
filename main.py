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
        1: "https://api.memegen.link/images/stonks.png?height=300&width=300",
        2: "https://api.memegen.link/images/cheems/it's_gooood.jpg?height=300&width=300",
        3: "https://api.memegen.link/images/fine/this_is_fine.jpg?height=300&width=300",
        4: "https://api.memegen.link/images/grave/_/5th_place/4th_place.jpg?height=300&width=300",
        5: "https://api.memegen.link/images/ugandanknuck/5th_place/it's_okay_just_10_lp.png?height=300&width=300",
        6: "https://api.memegen.link/images/disastergirl/7th_place/me.jpg?height=300&width=300",
        7: "https://api.memegen.link/images/ds/7th_place/8th_place.png?height=300&width=300",
        8: "https://api.memegen.link/images/buzz/you_see_that_woody/you_are_at_the_bottom.png?height=300&width=300",
        9: "https://api.memegen.link/images/woman-cat/why_is_it_not_working/error.jpg?height=300&width=300",
    }
    # Return the meme URL based on placement, default to the last meme if not found
    return meme_urls.get(placement, meme_urls[9])


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

    # Extract LP from player_rating and ranking text
    # player_rating_text = latest_match.get("summary", {}).get("player_rating", "")
    # ranked_rating_text = ranked.get("rating_text", "")

    player_rating_text = latest_match.get("summary", {}).get("player_rating_numeric", "")
    ranked_rating_text = ranked.get("rating_numeric", "")


    try:
        lp_difference = int(ranked_rating_text) - int(player_rating_text)
    except:
        lp_difference = 0
    # Get the meme URL based on placement
    meme_image = get_meme_url_by_placement(latest_match.get("placement", 9))

    stats = {
        "username": summoner.get("riot_id", "").split("#")[0],
        "tag": summoner.get("riot_id", "").split("#")[1],
        "rank": ranked.get("rating_text", "Unranked"),
        "time": time_elapsed_formatted,
        "duration": time_eliminated_formatted,
        "lp_change": f"{'-' if lp_difference < 0 else '+'}{abs(lp_difference)} LP",
        "lp_change_color": get_lp_change_color(lp_difference),  # Determine color
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
            "url": "https://rerollcdn.com/characters/Skin/12/Norra.png",
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
            background-color: #2c344f;
            color: #ffffff;
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
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .meme-image {
            flex-shrink: 0;
            margin-right: 20px;
            width: 200px;
            height: 200px;
            overflow: hidden;
            border-radius: 8px;
            background-color: transparent;
        }
        .meme-image img {
            width: 115%;
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
            color: #ffffff;
        }
        .ranked-info {
            font-size: 18px;
            margin-bottom: 5px;
            color: #ffffff;
        }
        .rank-rating-label {
            color: #cc583f; /* Bright green color for the rank rating label */
            font-weight: bold;
        }
        .highlight {
            font-size: 36px;
            font-weight: bold;
            color: #ff6347;
        }
        
        .username-tag {
            text-align: left;
            font-size: 20px;
            color: #ffffff;
        }
        .username-tag .username {
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
            padding-top: 10px;
        }
        .champion-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 60px;
        }
        .champion-icon {
            width: 60px;
            height: 60px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        .price-1 {
            border: 2px solid #ffffff; /* White */
        }

        .price-2 {
            border: 2px solid #00ff00; /* Green */
        }

        .price-3 {
            border: 2px solid #0000ff; /* Blue */
        }

        .price-4 {
            border: 2px solid #800080; /* Purple */
        }

        .price-5 {
            border: 2px solid #ffd700; /* Gold */
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
    </style>
</head>
<body>
    <div class="container">
        <div class="meme-image">
            <img src="{{ meme_image }}" alt="Meme Image">
        </div>

        <div class="content">
            <div class="header">
                <div class="stats">
                    <div class="ranked-info">
                        <span class="rank-rating-label">Rank rating:</span> {{ ranked.rating_text }}
                    </div>
                    <div class="ranked-info">Time: {{ stats.time }}</div>
                    <div class="ranked-info">Match duration: {{ stats.duration }}</div>
                    <div class="ranked-info">LP Change: <span class="highlight" style="color: {{ stats.lp_change_color }};">{{ stats.lp_change }}</span></div>
                </div>

                <div class="username-tag">
                    <div class="username">
                        <span class="username-label">RiotID:</span> {{ summoner_name }}#{{ tag }}
                    </div>
                    <div class="placement">{{ placement }}{{ ordinal }}</div>
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

    # Generate the ordinal suffix for the placement
    placement = latest_match["placement"]
    ordinal_suffix = get_ordinal_suffix(placement)

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
        ranked=ranked,  # Ensure ranked is passed to the template
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
    riot_id = "Mawinner"
    tag = "1402"
    profile_data = get_tft_profile(riot_id, tag)

    create_match_summary(profile_data,True)

    # create_match_summary(profile_data, True)