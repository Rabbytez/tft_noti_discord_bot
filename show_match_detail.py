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