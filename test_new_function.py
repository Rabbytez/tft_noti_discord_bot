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
        </div>
    </body>
    </html>
    """

    # Render the HTML with Jinja2
    template = Template(html_template)
    rendered_html = template.render(
        formatted_units=formatted_units,
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

# Test with your JSON data
with open("v2_profile_data_beggy_3105.json", "r", encoding="utf-8") as f:
    profile_data = json.load(f)

create_match_summary(profile_data)