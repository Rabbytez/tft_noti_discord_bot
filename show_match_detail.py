import requests
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from jinja2 import Template
from json_create_dict import organize_stage_data
import time
import random

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


