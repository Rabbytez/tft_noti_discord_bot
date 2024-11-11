from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections.abc import Iterable
import time
import os
import json
from chamption_assets import get_champion_assets

def create_match_summary(profile_data):
    # Accessing profile and summoner info
    profile = profile_data.get("data", {}).get("tft", {}).get("profile", [{}])[0]
    profile_data = profile.get("profile", {})
    summoner_info = profile_data.get("summonerInfo", {})

    # Accessing latest match from entries
    latest_match = profile_data.get("summonerProgressTracking", {}).get("progress", {}).get("entries", [{}])[0]

    # Summoner details
    summoner_name = summoner_info.get("gameName", "")
    summoner_tag = summoner_info.get("tagLine", "")
    summoner_icon = summoner_info.get("profileIcon", "")
    puuid = summoner_info.get("puuid", "")

    # Match details
    placement = latest_match.get("placement", 0)
    traits = latest_match.get("traits", [])
    units = latest_match.get("units", [])
    lp_info = latest_match.get("lp", {}).get("after", {})
    lp_diff = latest_match.get("lp", {}).get("lpDiff", 0)

    # Formatting traits and units for display
    formatted_traits = [f"{trait['slug'].capitalize()} ({trait['numUnits']} units)" for trait in traits]
    formatted_units = []
    for unit in units:
        unit_name = unit["slug"].capitalize()
        unit_items = unit.get("items", [])
        
        # Debugging: Check the type of unit.items
        print(f"Unit: {unit_name} - Items Type: {type(unit_items)} - Items: {unit_items}")
        
        # If unit.items is None or not a list, make it an empty list
        if unit_items is None or not isinstance(unit_items, list):
            unit_items = []

        # Collect item details (name and dynamically generate image URL)
        items_info = []
        for item_name in unit_items:
            # Construct the URL using the item name, converting spaces to dashes if necessary
            item_image_url = f"https://cdn.mobalytics.gg/assets/tft/images/game-items/set12/{item_name.lower().replace(' ', '-')}.png?v=60"
            items_info.append({
                "name": item_name,
                "url": item_image_url
            })

        formatted_units.append({
            "name": unit_name,
            "tier": "★" * unit.get("tier", 1),
            "items": items_info  # Store item details (name and dynamically generated image URL)
        })

    # Debugging: Print final data passed to the template
    print(f"Formatted Units: {formatted_units}")

    # Populate champions data using champion_assets
    champion_assets = get_champion_assets()
    champions = []
    for unit in units:
        champion_name = unit["slug"].capitalize()
        champion_info = champion_assets.get(champion_name, {"url": "https://via.placeholder.com/50", "price": "N/A"})
        champions.append({
            "icon": champion_info["url"],
            "stars": "★" * unit.get("tier", 1),
            "price": champion_info["price"]
        })

    # LP and rank details
    rank_tier = lp_info.get("rank", {}).get("tier", "Unranked")
    print(rank_tier)
    rank_division = lp_info.get("rank", {}).get("division", "")
    lp_value = lp_info.get("value", 0)

    # HTML Template for match summary with champion-list section
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Match Summary</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #1c1c1e; color: #f7f7f7; }
            .summary { border: 1px solid #ccc; padding: 20px; margin: 20px; background-color: #2c2f33; }
            .title { font-size: 24px; font-weight: bold; margin-bottom: 10px; color: #ffd700; }
            .info { font-size: 18px; margin: 5px 0; }
            .traits, .units, .champion-list { margin-top: 10px; }
            .unit-item { margin: 5px 0; }
            .rank { font-weight: bold; color: #4caf50; }
            .champion-item { display: inline-block; margin: 5px; }
            .champion-icon img { width: 50px; height: 50px; }
        </style>
    </head>
    <body>
        <div class="summary">
            <div class="title">Match Summary</div>
            <div class="info">Summoner: {{ summoner_name }}#{{ summoner_tag }}</div>
            <div class="info">Rank: <span class="rank">{{ rank_tier }} {{ rank_division }}</span> ({{ lp_value }} LP)</div>
            <div class="info">LP Change: {{ lp_diff }}</div>
            <div class="info">Placement: {{ placement }}</div>

            <div class="traits">
                <div class="title">Traits</div>
                <ul>
                    {% for trait in formatted_traits %}
                    <li>{{ trait }}</li>
                    {% endfor %}
                </ul>
            </div>

            <div class="units">
                <div class="title">Units</div>
                <ul>
                    {% for unit in formatted_units %}
                    <li class="unit-item">
                        <strong>{{ unit.name }}</strong> (Tier: {{ unit.tier }})<br>
                        Items: 
                        {% if unit.items %}
                            <ul>
                                {% for item in unit.items %}
                                    <li>
                                        <img src="{{ item.url }}" alt="{{ item.name }}" style="width: 30px; height: 30px;"> 
                                        {{ item.name }}
                                    </li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            None
                        {% endif %}
                    </li>
                    {% endfor %}
                </ul>
            </div>

                        
            <div class="champion-list">
                <div class="title">Champions</div>
                {% for champion in champions %}
                <div class="champion-item">
                    <div class="champion-icon price-{{ champion.price }}">
                        <img src="{{ champion.icon }}" alt="Champion Icon" onerror="this.onerror=null; this.src='https://via.placeholder.com/50';">
                    </div>
                    <div class="champion-stars">{{ champion.stars }}</div>
                </div>
                {% endfor %}
            </div>
            {% for unit in units %}
                <h2>{{ unit.name }}</h2>
                <ul>
                    {% for item in unit['items'] %}
                        <li>{{ item.name }} - <img src="{{ item.url }}"></li>
                    {% endfor %}
                </ul>
            {% endfor %}
        </div>
    </body>
    </html>
    """

    # Render the HTML with Jinja2
    template = Template(html_template)
    rendered_html = template.render(
        units=formatted_units,  # Changed this line
        summoner_name=summoner_name,
        summoner_tag=summoner_tag,
        rank_tier=rank_tier,
        rank_division=rank_division,
        lp_value=lp_value,
        lp_diff=lp_diff,
        placement=placement,
        formatted_traits=formatted_traits,
        champions=champions
    )
    print(rendered_html)
    # Create 'outputs' folder if it does not exist
    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    # Save HTML to the outputs folder
    html_path = os.path.join(output_folder, "match_summary.html")
    with open(html_path, "w", encoding="utf-8") as file:
        file.write(rendered_html)

    # Set up Chrome options for headless screenshot
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("file://" + os.path.abspath(html_path))
        time.sleep(1)

        # Capture a screenshot of the .summary div element
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "summary"))
        )

        image_name = f"match_summary_{puuid}.png"
        screenshot_path = os.path.join(output_folder, image_name)
        container.screenshot(screenshot_path)
        print(f"Saved banner to {screenshot_path}")
        return screenshot_path
    finally:
        driver.quit()
        os.remove(html_path)

# Match details
def format_match_details(latest_match, items_data):
    # Validate inputs
    if not isinstance(latest_match, dict):
        raise ValueError("latest_match must be a dictionary")
    if not isinstance(items_data, dict):
        raise ValueError("items_data must be a dictionary")

    # Create item name to slug mapping
    item_name_to_slug = {
        item['flatData']['name']: item['flatData']['slug']
        for item in items_data.get('data', {}).get('items', [])
    }

    # Extract match details with proper defaults
    placement = int(latest_match.get("placement", 0))
    traits = list(latest_match.get("traits", []))
    units = list(latest_match.get("units", []))
    lp_info = dict(latest_match.get("lp", {}).get("after", {}))
    lp_diff = int(latest_match.get("lp", {}).get("lpDiff", 0))

    # Format traits ensuring list output
    formatted_traits = [
        f"{trait['slug'].capitalize()} ({trait['numUnits']} units)" 
        for trait in traits if isinstance(trait, dict)
    ]

    # Format units
    formatted_units = []
    for unit in units:
        if not isinstance(unit, dict):
            continue
            
        unit_name = unit.get("slug", "").capitalize()
        unit_items = list(unit.get("items", []))
        
        # Process items
        items_info = []
        for item_name in unit_items:
            if not isinstance(item_name, str):
                continue
                
            try:
                item_slug = item_name_to_slug.get(item_name)
                item_image_url = (
                    f"https://cdn.mobalytics.gg/assets/tft/images/game-items/set12/"
                    f"{item_slug or item_name.lower().replace(' ', '-')}.png?v=60"
                )
                
                items_info.append({
                    "name": str(item_name),
                    "url": str(item_image_url)
                })
            except (AttributeError, TypeError) as e:
                print(f"Error processing item {item_name}: {str(e)}")
                continue

        formatted_units.append({
            "name": unit_name,
            "items": items_info
        })

    # Return validated data structure
    return {
        "placement": placement,
        "traits": formatted_traits,
        "units": formatted_units,
        "lp_info": lp_info,
        "lp_diff": lp_diff
    }

# Test with your JSON data
with open("v2_profile_data_beggy_3105.json", "r", encoding="utf-8") as f:
    profile_data = json.load(f)

create_match_summary(profile_data)