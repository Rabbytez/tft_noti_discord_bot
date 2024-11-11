import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    formatted_traits = [
        f"{trait['slug'].capitalize()} ({trait['numUnits']} units)"
        for trait in traits if isinstance(trait, dict)
    ]
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
        "traits": formatted_traits,
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

    # Access 'summonerProgressTracking' directly
    latest_match = summoner_info.get("summonerProgressTracking", {}).get("progress", {}).get("entries", [{}])[0]

    # Get rank information
    rank_icon, rank_color, rank_tier = get_rank_icon_and_color(rating_text)
    lp_diff = latest_match.get("lp", {}).get("lpDiff", 0)
    lp_value = latest_match.get("lp", {}).get("after", {}).get("value", 0)
    lp_color = get_lp_change_color(lp_diff)

    # Format match details
    placement = latest_match.get("placement", 0)
    traits = latest_match.get("traits", [])
    champs = latest_match.get("units", [])
    
    # HTML template
    html_template = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TFT Match Summary</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .match-summary {
            background-color: #2e2e2e;
            border-radius: 10px;
            padding: 20px;
            width: 700px;
            display: flex;
            align-items: center;
            color: #fff;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        }

        .match-summary .rank {
            font-size: 1.2em;
            color: #8aeb7f;
            margin-bottom: 5px;
        }

        .match-summary img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-right: 15px;
        }

        .rank-icon {
            font-weight: bold;
            color: #8aeb7f;
            display: flex;
            align-items: center;
            font-size: 1em;
            margin-right: 10px;
        }

        .rank-icon img {
            width: 20px;
            height: 20px;
            margin-right: 5px;
        }

        .summary-details {
            flex: 1;
            padding: 0 15px;
        }

        .player-info {
            font-size: 1.5em;
            font-weight: bold;
            color: #fdd835;
            display: flex;
            align-items: center;
        }

        .lp-change {
            font-size: 1.2em;
            font-weight: bold;
            color: red;
            margin-top: 5px;
        }

        .match-info {
            color: #bbb;
            font-size: 0.9em;
            margin-top: 5px;
        }

        .champion-list {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .champion {
            text-align: center;
            position: relative;
        }

        .champion img {
            width: 50px;
            height: 50px;
            border-radius: 8px;
        }

        .champion .stars {
            font-size: 0.8em;
            color: gold;
            font-weight: bold;
            position: absolute;
            bottom: -5px;
            left: 50%;
            transform: translateX(-50%);
        }
    </style>
</head>
<body>

<div class="match-summary">
    <img src="https://example.com/path-to-image.png" alt="Profile Picture">
    
    <div class="summary-details">
        <div class="player-info">beggy#3105 <span style="font-size: 0.8em; color: #bbb; margin-left: 5px;">3rd</span></div>
        
        <div class="rank-icon">
            <img src="https://example.com/path-to-rank-icon.png" alt="Rank Icon">
            EMERALD IV 5 LP
        </div>
        
        <div class="match-info">
            Time: 47m 48s ago<br>
            Match Duration: 34m 8s
        </div>
        
        <div class="lp-change">LP: -15 LP</div>
        
        <div class="champion-list">
            <div class="champion">
                <img src="https://example.com/path-to-champion1.png" alt="Champion 1">
                <div class="stars">★★★</div>
            </div>
            <div class="champion">
                <img src="https://example.com/path-to-champion2.png" alt="Champion 2">
                <div class="stars">★★</div>
            </div>
            <!-- Add more champions similarly -->
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
    )

    # Save the rendered HTML to a file
    html_file = 'match_summary.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    # Use Selenium to open the HTML and take a screenshot
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        driver.set_window_size(1024, 768)
        driver.get(f'file:///{os.path.abspath(html_file)}')
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'champion-list'))
        )
        screenshot_file = 'match_summary.png'
        driver.save_screenshot(screenshot_file)
        print(f"Screenshot saved as {screenshot_file}")
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
    finally:
        driver.quit()

# Test with your JSON data
if __name__ == '__main__':
    with open("v2_profile_data_beggy_3105.json", "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    create_match_summary(profile_data)
