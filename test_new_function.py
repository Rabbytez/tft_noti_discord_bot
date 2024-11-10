from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json

def create_match_summary(profile_data):
    # Accessing profile and summoner info
    profile = profile_data.get("data", {}).get("tft", {}).get("profile", [{}])[0]
    profile_data = profile.get("profile", {})
    summoner_info = profile_data.get("summonerInfo", {})

    # Accessing latest match from entries
    latest_match = profile.get("summonerProgressTracking", {}).get("progress", {}).get("entries", [{}])[0]

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
    formatted_units = [{
        "name": unit["slug"].capitalize(),
        "tier": "★" * unit.get("tier", 1),
        "items": unit.get("items", [])
    } for unit in units]

    # LP and rank details
    rank_tier = lp_info.get("rank", {}).get("tier", "Unranked")
    rank_division = lp_info.get("rank", {}).get("division", "")
    lp_value = lp_info.get("value", 0)

    # HTML Template for match summary
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
            .traits, .units { margin-top: 10px; }
            .unit-item { margin: 5px 0; }
            .rank { font-weight: bold; color: #4caf50; }
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
                        Items: {{ unit.items | join(", ") if unit.items else "None" }}
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

    # Render the HTML with Jinja2
    template = Template(html_template)
    rendered_html = template.render(
        summoner_name=summoner_name,
        summoner_tag=summoner_tag,
        rank_tier=rank_tier,
        rank_division=rank_division,
        lp_value=lp_value,
        lp_diff=lp_diff,
        placement=placement,
        formatted_traits=formatted_traits,
        formatted_units=formatted_units
    )

    # Save HTML and generate a screenshot
    with open("match_summary.html", "w", encoding="utf-8") as file:
        file.write(rendered_html)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("file://" + os.path.abspath("match_summary.html"))
        time.sleep(1)

        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "summary"))
        )

        image_name = f"match_summary_{puuid}.png"
        container.screenshot(image_name)
        print(f"Saved banner to {image_name}")
        return image_name
    finally:
        driver.quit()
        os.remove("match_summary.html")

# Test with your JSON data
with open("v2_profile_data_beggy_3105.json", "r", encoding="utf-8") as f:
    profile_data = json.load(f)

create_match_summary(profile_data)
