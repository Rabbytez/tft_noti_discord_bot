import os
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from main import get_profile_data, get_match_data
from jinja2 import Template
from datetime import datetime, timezone
from augments import augment_data
import pytz

# Import the assets functions
from assets import get_champion_assets, get_rank_assets , get_trait_data

# Load items data
with open("tft_set12_items.json", "r", encoding="utf-8") as f:
    items_data = json.load(f)

# Retrieve rank data and champion assets from assets.py
rank_data = get_rank_assets()
champion_assets = get_champion_assets()
trait_data = get_trait_data()

def time_ago(match_time_str):
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    # Parse the match time string into a datetime object
    match_time = datetime.strptime(match_time_str, "%Y-%m-%dT%H:%M:%SZ")
    match_time = match_time.replace(tzinfo=timezone.utc)

    # Convert match time to Bangkok timezone
    match_time = match_time.astimezone(bangkok_tz)

    # Get the current time in Bangkok timezone
    current_time = datetime.now(bangkok_tz)

    # Calculate the difference
    time_diff = current_time - match_time

    # Format the difference in a human-readable way
    days = time_diff.days
    seconds = time_diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if days > 0:
        return f"{days} days ago"
    elif hours > 0:
        return f"{hours} hours ago"
    elif minutes > 0:
        return f"{minutes} minutes ago"
    else:
        return "just now"
    
# Function to get rank icon and color
def get_rank_icon_and_color(rating_text):
    if not rating_text:
        return "", "#ffffff", ""
    parts = rating_text.strip().split(" ")
    rank = parts[0].title() if len(parts) > 0 else ""
    rank_roman = " ".join(parts[1:]) if len(parts) > 1 else ""
    rank_info = rank_data.get(rank, {"icon": "", "color": "#ffffff"})
    return rank_info["icon"], rank_info["color"], rank_roman

# Function to get LP change color
def get_lp_change_color(lp_change):
    """Return a CSS class based on LP change."""
    return "green" if lp_change > 0 else "red"

def puid_validation_profile_data(profile_data):
    summoner_profile = profile_data.get("data", {}).get("tft", {}).get("profile", [])
    summoner_info = summoner_profile[0].get("profile", {})
    puid_user = summoner_info.get("summonerInfo", {}).get("puuid", "")
    return puid_user

def puid_validation(puid_user,match_data):
    puid_user = puid_validation_profile_data(profile_data)
    print("PUID user " + puid_user)
    match_data_profile = match_data.get("data", {}).get("tft", {}).get("matchV2", [])
    get_all_match = match_data_profile.get("participants", {})

    for match in get_all_match:
        puid = match.get("puuid", "")
        if puid == puid_user:
            user_latest_match_data_details = match
            print("PUID found")
            return user_latest_match_data_details
        
def get_match_latest_id(profile_data):
    try:
        summoner_profile = profile_data.get("data", {}).get("tft", {}).get("profile", [])
        if not summoner_profile:
            return ""
            
        summoner_info = summoner_profile[0].get("profile", {})
        entries = summoner_info.get("summonerProgressTracking", {}).get("progress", {}).get("entries", [])
        
        # Check if there are any entries
        if entries and isinstance(entries, list) and len(entries) > 0:
            return entries[0].get("id", "")
            
        return ""
        
    except (IndexError, KeyError, TypeError) as e:
        print(f"Error getting match ID: {e}")
        return ""

# Function to format match details
def format_match_details(latest_match, items_data, user_latest_match_data_details):
    # Start timing this function
    start_time = time.time()

    # Get the latest match details
    latest_match_details = user_latest_match_data_details
    
    # Create item name to slug mapping
    item_name_to_slug = {
        item['flatData']['name']: item['flatData']['slug']
        for item in items_data['data']['items']
    }

    placement = latest_match.get("placement", 0)
    traits = latest_match.get("traits", [])
    champs = latest_match.get("units", [])
    lp_info = latest_match.get("lp", {}).get("after", {})
    lp_diff = latest_match.get("lp", {}).get("lpDiff", 0)

    # Function to get the color based on the number of units
    def get_trait_color(trait_slug, num_units):
        tiers = trait_data.get(trait_slug, {})
        for units, color in sorted(tiers.items(), key=lambda x: int(x[0]), reverse=True):
            if num_units >= int(units):
                return color
        return color

    # Formatting traits
    sorted_traits = sorted(traits, key=lambda x: x.get('numUnits', 0), reverse=True)
    url_img = "https://cdn.mobalytics.gg/assets/common/icons/tft-synergies-set12/"
    formatted_traits = []
    for trait in sorted_traits:
        if isinstance(trait, dict):
            trait_slug = trait.get('slug', '')
            trait_num_units = trait.get('numUnits', 0)
            trait_icon_url = f"{url_img}24-{trait_slug}.svg?v=61"
            trait_color = get_trait_color(trait_slug, trait_num_units)
            
            if trait_color != "default":
                formatted_traits.append({
                    "name": trait_slug.capitalize(),
                    "num_units": trait_num_units,
                    "icon_url": trait_icon_url,
                    "color": trait_color
                })

    formatted_champs = []
    for champ in champs:
        if not isinstance(champ, dict):
            continue
        champ_name = champ.get("slug", "").capitalize()
        champ_items = champ.get("items", [])

        # Ensure champ_items is a list
        if not isinstance(champ_items, list):
            champ_items = []

        # Collect item details
        items_info = []
        for item_name in champ_items:
            if not isinstance(item_name, str):
                continue
            item_slug = item_name_to_slug.get(item_name)
            if item_slug:
                item_image_url = f"https://cdn.mobalytics.gg/assets/tft/images/game-items/set12/{item_slug}.png?v=60"
            else:
                # Fallback
                item_image_url = f"https://cdn.mobalytics.gg/assets/tft/images/game-items/set12/{item_name.lower().replace(' ', '-')}.png?v=60"

            items_info.append({
                "name": item_name,
                "url": item_image_url
            })
        
        # Process augments
        augments_info = latest_match_details.get("augments", [])
        formatted_augments = []
        for augment in augments_info:
            augment_slug = augment.get("slug", "")
            augment_name = augment_slug.replace("-", " ").replace("+", "").title()  # Capitalize each word
            augment_image_url = augment_data(augment_name)
            formatted_augments.append({
                "name": augment_name,
                "url": augment_image_url
            })
        
        # Get champion image URL from assets
        champion_info = champion_assets.get(champ_name, {})
        champion_image_url = champion_info.get("url", "")
        champ_price = champion_info.get("price", 1)
        
        formatted_champs.append({
            "name": champ_name,
            "champ_price": champ_price,
            "items": items_info,
            "tier": "★" * champ.get("tier", 1),
            "image_url": champion_image_url
        })

    # End timing this function
    end_time = time.time()
    print(f"Time taken by format_match_details: {end_time - start_time:.4f} seconds")

    return {
        "placement": placement,
        "traits": formatted_traits,
        "augments": formatted_augments,
        "champs": formatted_champs,
        "lp_info": lp_info,
        "lp_diff": lp_diff
    }

# Function to create match summary
def create_match_summary(profile_data, match_data, user_latest_match_data_details):
    # Start timing this function
    start_time = time.time()

    # Extract necessary profile data
    summoner_profile = profile_data.get("data", {}).get("tft", {}).get("profile", [])
    summoner_info = summoner_profile[0].get("profile", {})
    summoner_name = summoner_info.get("info", {}).get("gameName", "")
    summoner_tag = summoner_info.get("info", {}).get("tagLine", "")
    rating_info = summoner_info.get("rank", {})
    rating_text = f"{rating_info.get('tier', '')} {rating_info.get('division', '')}"
    
    # Extract necessary match data
    latest_match_data = match_data.get("data", {}).get("tft", {}).get("matchV2", [])
    
    # Get the latest match time data
    match_time = time_ago(latest_match_data.get("date", {}))
    match_duration_seconds = latest_match_data.get("durationSeconds", 0)
    def format_duration(seconds):
        minutes = seconds // 60
        return f"{minutes}m"
    match_duration = format_duration(match_duration_seconds)
    
    # Extract profile icon ID and construct URL
    puid = summoner_info.get("summonerInfo", {}).get("puuid", "")
    profile_icon_id = summoner_info.get("summonerInfo", {}).get("profileIcon", "")
    profile_icon_url = f"https://cdn.mobalytics.gg/assets/lol/images/dd/summoner-icons/{profile_icon_id}.png?1"

    # Access 'summonerProgressTracking' directly
    latest_match = summoner_info.get("summonerProgressTracking", {}).get("progress", {}).get("entries", [{}])[0]

    # Get rank information
    rank_icon, rank_color, rank_tier = get_rank_icon_and_color(rating_text)
    lp_diff = latest_match.get("lp", {}).get("lpDiff", 0)
    lp_value = latest_match.get("lp", {}).get("after", {}).get("value", 0)
    lp_color = get_lp_change_color(lp_diff)
    
    # Get only the last two digits of lp_value
    lp_value_last_two_digits = lp_value % 100
    
    def add_plus_minus(lp_diff):
        if lp_color == "green":
            lp_diff = f"+{lp_diff}"
        else:
            lp_diff = f"{lp_diff}" 
        return lp_diff
    lp_diff = add_plus_minus(lp_diff)    

    # Get game mode
    check_game_mode = latest_match.get("lp", {}).get("after", {}).get("rank", {}).get("__typename", {})
    game_mode = ""
    if check_game_mode == "SummonerRank":
        game_mode = "Ranked"
    else:
        game_mode = "..."
    
    # Format match details
    match_details = format_match_details(latest_match, items_data,user_latest_match_data_details)
    
    ver_patch = latest_match.get("patch", "")
    
    placement = match_details["placement"]
    traits = match_details["traits"]
    augments = match_details["augments"]
    champs = match_details["champs"]

    # HTML template
    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,553;1,553&display=swap" rel="stylesheet">
    <title>Match Summary</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
        }
            
        .container {
            max-height: 325px;
            max-width: 845px;
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: "Noto Sans", serif;
            font-weight: 553;
            font-style: normal;
            padding: 25px;
            position: relative;
        }
    
        .match-summary {
            display: flex;
            position: relative;
            margin-top: 20px;
            align-items: start;
            justify-content: start;
            max-height: 195px;
        }

        .profile-info {
            display: flex;
            align-items: center;
        }
        .profile-info img {
            border-radius: 50%;
            width: 100px; /* Adjust the size as needed */
            height: 100px;
            object-fit: cover;
        }
        .summary-details {
            margin-left: 20px;
        }
        .profile-info {
            display: flex;
            align-items: start;
            height: 100%;
        }
        .profile-info img {
            border-radius: 4px;
            width: 175px;
            height: 175px;
            object-fit: cover;
            margin-right: 20px;
        }
        .lp-change .green {
            color: green;
        }
        .lp-change .red {
            color: red;
        }
        .champion-list {
            display: flex;
            flex-wrap: wrap;
            flex: 1;
        }
        .champion {
            position: relative;
            margin: 5px;
            text-align: center;
        }
        .champion-icon{
            width: 55px;
            height: 55px;
            border-radius: 10px;
        }
        .champion-icon img {
            width: 100%;
            height: 100%;
            border-radius: 6px;
        }
        .champion .stars {
            font-size: 1.0em;
            color: gold;
            font-weight: bold;
            position: absolute;
            bottom: 17px;
            left: 50%;
            transform: translateX(-50%);
        }
        .items {
            margin-top: 5px;
            display: flex;
            justify-content: center;
            
        }
        .items img {
            width: 16px;
            height: 16px;
            border: 0.5px solid #1a1a1a;
            margin: 0 1px;
        }
        .rank-icon {
            display: flex;
            align-items: center;
        }
        .rank-icon img {
            width: 20px;
            height: 20px;
            margin-right: 5px;
        }
        .stat-bar {
            display: flex;
            flex-direction: row;
            margin-bottom: 20px;
            max-height: 120px;
        }
        .stat-container {
            display: flex;
            flex-direction: column;
            align-items: start;
            justify-content: flex-end;
            margin-left: 25px;
            margin-right: 15px;
            align-items: flex-end;

        }
        .placement-container {
            display: flex;
            flex-direction: column;
            margin-left: 10px;
            align-items: center;
        }
        .placement-number {
            font-size: 3.2em;
            font-weight: bold;
            background: none;
            color: inherit;
        }
        .game-mode {
            display: contents;
            align-items: start;
            font-size: 1.6em;
            font-weight: bold;
        }
        .time-patch {
            font-size: 0.6em;
        }
        .first-container {
            display: flex;
            flex-direction: row;
            padding: 15px;
            align-items: center;
            justify-content: space-between;
            background-color: #2e2e2e;
            border-radius: 10px;
        }
        .augments-container {
            display: flex;
            align-items: stretch;
            background-color: #2e2e2e;
            border-radius: 10px;
            margin-left: 25px;
        }

        .augment-label {
            writing-mode: vertical-rl;
            text-orientation: mixed;
            transform: rotate(180deg);
            background-color: #9d3f3f;
            color: #ffffff;
            padding: 10px;
            font-size: 0.8em;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 0 10px 10px 0;
        }
        .augments-detail {
            display: flex;
            flex-direction: column;
            align-items: start;
            justify-content: center;
            max-width: 150px;
            padding: 15px 15px 15px 8px;
            background-color: #2e2e2e;
            border-radius: 10px;
        }
        .augment {
            display: flex;
            align-items: center;
        }
        .augment img {
            width: 35px;
            height: 35px;
            margin: 0 2px;
        }
        .augment-text {
            font-size: 0.6em;
            text-align: start;
            margin-right: 5px;
        }
        .glow-container {
            position: absolute;
            display: contents;
            box-shadow: 0 0 10px rgba(255, 140, 0, 0.8), 0 0 20px rgba(255, 0, 0, 0.6);
            border-radius: 10px; 
            padding: 5px; 
        }        
        .traits-list {
            display: flex;
            flex: 1;
            max-width: 400px;
            padding: 5px 10px 10px 25px;
            align-items: flex-start;
            flex-wrap: wrap;
            justify-content: flex-start;
            align-content: flex-start;
        }
        .trait {
            display: flex;
            align-items: center;
            margin-right: 10px;
            margin-bottom: 10px;
            padding: 5px;
            border-radius: 5px;
        }
        .trait img {
            width: 18px;  /* Adjust size as needed */
            height: 18px;
            margin-right: 5px;
        }
        .trait-text {
            font-size: 0.6em;  /* Smaller text size */
            text-align: center;
        }
        .trait-num-units {
            font-size: 0.6em;  /* Smaller text size */
            margin-left: 4px;
            margin-right: 4px;
        }
        .player-tag {
            font-size: 0.75em;
            color: #838383;
        }
        .silver { background-color: #6b6b6b; }
        .gold { background-color: #dbaf0d; }
        .prismatic { background-color: #8432ab; }
        .copper { background-color: #b87333; }
        .default { background-color: black; color: white; }
        .price-1 {
            border: 3.5px solid silver;
        }
        .price-2 {
            border: 3.5px solid green;
        }
        .price-3 {
            border: 3.5px solid blue;
        }
        .price-4 {
            border: 3.5px solid purple;
        }
        .price-5 {
            border: 3.5px solid #dbaf0d;
        }
        .placement-1 {
        color: #ebe729;
        text-shadow: 0 0 40px rgb(247 217 59 / 91%), 0 0 55px rgb(255 239 92), 0 0 55px rgb(255 233 31);
        }
        
        /* Placement color and gradient for ranks 2-4 */
        .placement-2 {
            color: #ffe940;
            text-shadow: 0 0 30px rgb(219 179 24 / 76%), 0 0 35px rgb(201 158 16 / 80%);
        }
        .placement-3 {
            color: #ff9c1c;
            text-shadow: 0 0 30px rgb(195 109 0 / 76%), 0 0 35px rgb(201 158 16 / 80%);
        }
        .placement-4 {
            color: #ff7007;
            text-shadow: 0 0 30px rgb(195 109 0 / 76%), 0 0 35px rgb(201 158 16 / 80%);
        }
        
        /* Placement color and gradient for ranks 5-8 */
        .placement-5 {
            color: #f3f3f3;
            text-shadow: 0 0 30px rgb(211 0 0 / 60%), 0 0 35px rgb(217 131 131 / 80%);
        }
        .placement-6 {
            color: #f3f3f3;
            text-shadow: 0 0 30px rgb(211 0 0 / 70%), 0 0 35px rgb(217 131 131 / 80%);
        }
        .placement-7 {
            color: #f3f3f3;
            text-shadow: 0 0 30px rgb(211 0 0 / 80%), 0 0 35px rgb(217 131 131 / 80%);
        }
        .placement-8 {
            color: #f3f3f3;
            text-shadow: 0 0 30px rgb(247 19 19 / 80%), 0 0 45px rgb(247 19 19 / 80%), 0 0 45px rgb(247 19 19 / 80%);
        }
    </style>
</head>
<body>
<div class="container">
    <div class="stat-bar">
        <div class="first-container">
            <div class="placement-container">
                <div class="placement-number placement-{{ placement }}">{{ placement }}</div>
                <div class="lp-change"><span class="{{ lp_color }}">{{ lp_diff }} LP</span></div>
            </div>
            <div class="stat-container">
                <div class="time-patch">{{ ver_patch }} ∙ {{ match_time }} ∙ {{ match_duration }}</div>
                <div class="game-mode">{{ game_mode }}</div>
                <div class="rank-icon">
                    <img src="{{ rank_icon }}" alt="Rank Icon">
                    {{ rank_tier }} {{ lp_value }} LP
                </div>
                <div class="player-tag">{{ summoner_name }}<span>#{{ summoner_tag }}</span></div>
            </div>
        </div>
        <div class="augments-container">
            <div class="augment-label">Augments</div>
            <div class="augments-detail">
                {% for augment in augments %}
                <div class="augment">
                    <img src="{{ augment.url }}" alt="{{ augment.name }}">
                    <div class="augment-text">{{ augment.name }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
            <div class="traits-list">
                {% for trait in traits %}
                    {% if trait.color %}  {# Only show traits with active style/color #}
                    <div class="trait {{ trait.color }}">
                        <img src="{{ trait.icon_url }}" alt="{{ trait.name }}">
                        <div class="trait-text">{{ trait.name }}</div>
                        <div class="trait-num-units">{{ trait.num_units }}</div>
                    </div>
                    {% endif %}
                {% endfor %}
            </div>
    </div>
    <div class="match-summary">
        <div class="profile-info">
            <img src="{{ profile_icon_url }}" alt="Profile Picture">
        </div>
        <div class="champion-list">
            {% for champ in champs %}
            <div class="champion">
                <div class="champion-icon price-{{ champ.champ_price }}">
                    <img src="{{ champ.image_url }}" alt="{{ champ.name }}">
                </div>
                <div class="stars">{{ champ.tier }}</div>
                <div class="items">
                    {% for item in champ['items'] %}
                    <img src="{{ item.url }}" alt="{{ item.name }}">
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
</body>
</html>
'''
    # Render the HTML with Jinja2
    template = Template(html_template)
    rendered_html = template.render(
        champs=champs,
        traits=traits,
        augments=augments,
        placement=placement,
        lp_diff=lp_diff,
        lp_color=lp_color,
        rank_icon=rank_icon,
        rank_color=rank_color,
        rank_tier=rank_tier,
        lp_value=lp_value_last_two_digits,
        summoner_name=summoner_name,
        summoner_tag=summoner_tag,
        rating_text=rating_text,
        profile_icon_url=profile_icon_url,
        game_mode=game_mode,
        match_time=match_time,
        match_duration=match_duration,
        ver_patch=ver_patch
    )

    # Save the rendered HTML to a file
    html_file = 'match_summary.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    # Start timing Selenium operations
    selenium_start_time = time.time()

    # Use Selenium to open the HTML and take a screenshot
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(f'file:///{os.path.abspath(html_file)}')
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container"))
        )
        image_name = f"match_summary_banner_{puid}.png"
        screenshot_path = image_name
        container.screenshot(screenshot_path)
        print(f"Saved banner to {screenshot_path}")
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
    finally:
        driver.quit()

    # End timing Selenium operations
    selenium_end_time = time.time()
    print(f"Selenium operations took {selenium_end_time - selenium_start_time:.4f} seconds")

    # End timing this function
    end_time = time.time()
    print(f"Time taken by create_match_summary: {end_time - start_time:.4f} seconds")

# Test with your JSON data
if __name__ == '__main__':
    total_start_time = time.time()  # Start total execution timing

    riotname = "beggy"
    tag = "3105"

    try:
        data_fetch_start_time = time.time()  # Start data fetching timing
        profile_data = get_profile_data(riotname, tag)

        data_fetch_end_time = time.time()  # End data fetching timing
        print(f"Data fetching took {data_fetch_end_time - data_fetch_start_time:.4f} seconds")

    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
        
    match_id = get_match_latest_id(profile_data)
    match_data = get_match_data(match_id, riotname, tag)
    puid_user = puid_validation_profile_data(profile_data)
    user_latest_match_data_details = puid_validation(puid_user,match_data)

    create_match_summary(profile_data, match_data, user_latest_match_data_details)

    total_end_time = time.time()  # End total execution timing
    print(f"Total script execution time: {total_end_time - total_start_time:.4f} seconds")
