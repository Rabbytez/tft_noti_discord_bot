import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from main import get_profile_data,get_match_data 
from jinja2 import Template

# Import the assets functions
from assets import get_champion_assets, get_rank_assets

# Load items data
with open("tft_set12_items.json", "r", encoding="utf-8") as f:
    items_data = json.load(f)

# Retrieve rank data and champion assets from assets.py
rank_data = get_rank_assets()
champion_assets = get_champion_assets()

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

def puid_validation(profile_data):
    summoner_profile = profile_data.get("data", {}).get("tft", {}).get("profile", [])
    summoner_info = summoner_profile[0].get("profile", {})
    puid = summoner_info.get("summonerInfo", {}).get("puuid", "")
    return puid

# Function to format match details
def format_match_details(latest_match, items_data):
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

    # Formatting traits
    url_img = f"https://raw.githubusercontent.com/Rabbytez/tft12_trait_rab/refs/heads/main/trait_img/"
    formatted_traits = []
    for trait in traits:
        if isinstance(trait, dict):
            trait_slug = trait.get('slug', '').capitalize()
            trait_num_units = trait.get('numUnits', 0)
            parse_icon_url = f"{url_img}TFT12_{trait_slug}_{trait_num_units}.png"
            trait_icon_url = parse_icon_url

            formatted_traits.append({
                "name": trait_slug,
                "num_units": trait_num_units,
                "icon_url": trait_icon_url
            })
    print(formatted_traits)
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
            
        # Get champion image URL from assets
        champion_info = champion_assets.get(champ_name, {})
        champion_image_url = champion_info.get("url", "")

        formatted_champs.append({
            "name": champ_name,
            "items": items_info,
            "tier": "★" * champ.get("tier", 1),
            "image_url": champion_image_url
        })

    return {
        "placement": placement,
        "traits": trait_icon_url,
        "champs": formatted_champs,
        "lp_info": lp_info,
        "lp_diff": lp_diff
    }

# Function to create match summary
def create_match_summary(profile_data):
    # Extract necessary data
    summoner_profile = profile_data.get("data", {}).get("tft", {}).get("profile", [])
    summoner_info = summoner_profile[0].get("profile", {})
    summoner_name = summoner_info.get("info", {}).get("gameName", "")
    summoner_tag = summoner_info.get("info", {}).get("tagLine", "")
    rating_info = summoner_info.get("rank", {})
    rating_text = f"{rating_info.get('tier', '')} {rating_info.get('division', '')}"

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
    
    def add_plus_minus(lp_diff):
        if lp_color == "green":
            lp_diff = f"+{lp_diff}"
        else:
            lp_diff = f"-{lp_diff}" 
        return lp_diff
    lp_diff = add_plus_minus(lp_diff)    

    # Get game mode
    check_game_mode = latest_match.get("lp", {}).get("after", {}).get("rank", {}).get("__typename", {})
    print(check_game_mode)
    game_mode = ""
    if check_game_mode == "SummonerRank":
        game_mode = "Ranked"
    else:
        game_mode = "..."
    
    # Format match details
    match_details = format_match_details(latest_match, items_data)
    
    ver_patch = latest_match.get("patch", "")
    
    placement = match_details["placement"]
    traits = match_details["traits"]
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
            max-width: 760px;
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
        }
        .champion {
            position: relative;
            margin: 5px;
            text-align: center;
        }
        .champion img {
            width: 55px;
            height: 55px;
            border-radius: 10px;
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
            justify-content: start;
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

        }
        .traits-list {
            display: flex;
            max-width: 400px;
            padding: 15px;
            flex-wrap: wrap;
            margin-left: 25px;
            padding-bottom: 8px;
            background-color: #2e2e2e;
            border-radius: 10px;
            align-items: center;
        }

        .trait {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-right: 10px;
            margin-bottom: 10px;
        }

        .trait img {
            width: 24px; /* Base width */
            height: 24px; /* Base height */
            margin-bottom: 5px;
        }
        .trait-text {
            font-size: 0.6em;  /* Smaller text size */
            text-align: center;
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
        }
        .game-mode {
            display: contents;
            align-items: start;
            font-size: 1.5em;
            font-weight: bold;
        }
        .ver-patch {
            font-size: 0.8em;
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
        .augments-detail {
            display: flex;
            flex-direction: column;
            align-items: start;
            justify-content: start;
            max-width": 75px;
            background-color: #2e2e2e;
            border-radius: 10px;
        }
        .glow-container {
            position: absolute;
            display: contents;
            box-shadow: 0 0 10px rgba(255, 140, 0, 0.8), 0 0 20px rgba(255, 0, 0, 0.6);
            border-radius: 10px; 
            padding: 5px; 
        }
    </style>
</head>
<body>
<div class="container">
    <div class="stat-bar">
        <div class="first-container">
            <div class="placement-container">
                <div class="placement-number">{{ placement }}</div>
                <div class="lp-change"><span class="{{ lp_color }}">{{ lp_diff }} LP</span></div>
            </div>
            <div class="stat-container">
                <div class="ver-patch">{{ ver_patch }}</div>
                <div class="game-mode">{{ game_mode }}</div>
                <div class="player-info">{{ summoner_name }}#{{ summoner_tag }}</div>
                <div class="match-time">{{ match_time }}</div>
                <div class="rank-icon">
                    <img src="{{ rank_icon }}" alt="Rank Icon">
                    {{ rank_tier }} {{ lp_value }} LP
                </div>
            </div>
        </div>
        <div class="augments-detail">
            <!-- Augments details can be added here -->
        </div>
        <div class="traits-list">
            {% for trait in traits %}
            <div class="trait">
                <img src="{{ trait.icon_url }}" alt="{{ trait.name }}">
                <div class="trait-text">{{ trait.name }} ({{ trait.num_units }}) </div>
            </div>
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
                <img src="{{ champ.image_url }}" alt="{{ champ.name }}">
                    <div class="glow-container">
                        <div class="stars">{{ champ.tier }}</div>
                    </div>
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
        placement=placement,
        lp_diff=lp_diff,
        lp_color=lp_color,
        rank_icon=rank_icon,
        rank_color=rank_color,
        rank_tier=rank_tier,
        lp_value=lp_value,
        summoner_name=summoner_name,
        summoner_tag=summoner_tag,
        rating_text=rating_text,
        profile_icon_url=profile_icon_url,
        game_mode=game_mode,
        match_time="",
        ver_patch=ver_patch
    )

    # Save the rendered HTML to a file
    html_file = 'match_summary.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

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

# Test with your JSON data
if __name__ == '__main__':
    match_id = "42590337"
    riotname = "beggy"
    tag = "3105"

    profile_data = get_profile_data(riotname, tag)
    match_data = get_match_data(match_id,riotname, tag)
    
    create_match_summary(profile_data)
    puid_validation(profile_data)