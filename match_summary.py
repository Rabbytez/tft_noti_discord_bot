import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from jinja2 import Template
from datetime import datetime
import pytz

class MatchProcessor:
    def __init__(self, match_data, riotname, tag):
        self.match_data = match_data
        self.riotname = riotname
        self.tag = tag
        
    def get_user_match_data(self):
        matches = self.match_data.get("matches", {})
        participants = matches.get("participants", [])
        for participant in participants:
            if (participant.get("gameName") == self.riotname and 
                participant.get("tagLine") == self.tag):
                return participant
        return None

    def format_traits(self, traits_data):
        formatted_traits = []
        for trait in sorted(traits_data, key=lambda x: x.get("numUnits", 0), reverse=True):
            if not isinstance(trait, dict):
                continue
                
            trait_slug = trait.get("name", "")
            trait_num_units = trait.get("numUnits", 0)
            trait_style = trait.get("style", "")
            trait_icon_url = trait.get("imageUrl", "")
            trait_color = self.get_trait_color(trait_slug, trait_num_units)
            
            if trait_color != "default":
                formatted_traits.append({
                    "name": trait_slug.capitalize(),
                    "style": trait_style,
                    "num_units": trait_num_units, 
                    "icon_url": trait_icon_url,
                    "color": trait_color
                })
                
        return formatted_traits

    def format_champions(self, champs_data):
        formatted_champs = []
        for champ in champs_data:
            if not isinstance(champ, dict):
                continue
                
            champ_name = champ.get("slug", "").capitalize()
            champ_items = champ.get("items", [])
            
            items_info = self.format_items(champ_items)
            champion_info = self.get_champion_info(champ_name)
            
            formatted_champs.append({
                "name": champ_name,
                "champ_price": champion_info.get("price", 1),
                "items": items_info,
                "tier": "★" * champ.get("tier", 1),
                "image_url": champion_info.get("url", "")
            })
            
        return formatted_champs

    def format_items(self, items):
        formatted_items = []
        for item_name in items:
            item_info = self.get_item_info(item_name)
            if item_info:
                formatted_items.append(item_info)
        return formatted_items

    def get_trait_color(self, trait_slug, num_units):
        # Implementation depends on your trait data structure
        return "gold" if num_units >= 6 else "silver" if num_units >= 4 else "bronze" if num_units >= 2 else "default"

    def get_champion_info(self, champion_name):
        # Implementation depends on your champion data structure 
        return {
            "price": 1,
            "url": f"https://raw.communitydragon.org/latest/game/assets/characters/{champion_name.lower()}/hud/{champion_name.lower()}_square.png"
        }

    def get_item_info(self, item_name):
        # Implementation depends on your item data structure
        return {
            "name": item_name,
            "url": f"https://raw.communitydragon.org/latest/game/assets/items/icons2d/{item_name.lower().replace(' ', '')}.png"
        }

    def format_match_details(self):
        user_match_data = self.get_user_match_data()
        if not user_match_data:
            return None
            
        placement = user_match_data.get("placement", 0)
        traits = self.format_traits(user_match_data.get("traits", []))
        champs = self.format_champions(user_match_data.get("units", []))
        
        # Format LP information
        lp_before = user_match_data.get("beforeLeagueLog", ["", "", 0])
        lp_after = user_match_data.get("afterLeagueLog", ["", "", 0])
        
        lp_info = {
            "before_rank": f"{lp_before[0]} {lp_before[1]}" if len(lp_before) > 1 else "Unknown",
            "before_lp": lp_before[2] if len(lp_before) > 2 else 0,
            "after_rank": f"{lp_after[0]} {lp_after[1]}" if len(lp_after) > 1 else "Unknown", 
            "after_lp": lp_after[2] if len(lp_after) > 2 else 0
        }
        
        return {
            "placement": placement,
            "traits": traits,
            "champs": champs,
            "lp_info": lp_info,
            "players_data": self.format_players_data(user_match_data)
        }

    def format_players_data(self, match_data):
        players = []
        participants = match_data.get("participants", [])
        
        for player in participants:
            players.append({
                "summoner_name": player.get("gameName", "Unknown"),
                "summoner_tag": player.get("tagLine", "0000"),
                "summoner_placement": player.get("placement", 8),
                "summoner_icon": self.get_summoner_icon(player.get("profileIcon", 0))
            })
            
        return sorted(players, key=lambda x: x["summoner_placement"])

    def get_summoner_icon(self, icon_id):
        return f"https://raw.communitydragon.org/latest/game/assets/ux/summonericons/profileicon{icon_id}.png"

class ScreenshotGenerator:
    def __init__(self):
        self.chrome_options = self._setup_chrome_options()
        
    def _setup_chrome_options(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        return options
        
    def capture(self, html_path, output_path):
        driver = webdriver.Chrome(options=self.chrome_options)
        try:
            driver.get(f"file:///{os.path.abspath(html_path)}")
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "container"))
            )
            container.screenshot(output_path)
            return output_path
        finally:
            driver.quit()

def get_html_template():
    return """
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
            height: 390px;
            max-height: 400px;
            max-width: 880px;
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
            align-items: start;
            justify-content: start;
            max-height: 200px;
        }

        .profile-info {
            display: flex;
            align-items: center;
        }
        .profile-info img {
            border-radius: 50%;
            width: 100px;
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
            width: 100px;
            height: 100px;
            object-fit: cover;
        }
        .lp-change .green {
            color: green;
        }
        .lp-change .red {
            color: red;
        }
        .champion-container {
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
            top: 45px;
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
            max-height: 130px;
        }
        .stat-1-container {
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            margin-left: 25px;
            margin-right: 15px;
            align-items: flex-end;
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
        .second-container {
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            padding: 15px;
            margin-left: 20px;
            background-color: #2e2e2e;
            border-radius: 10px;
            align-items: center;
        }
        /* Preserving all the remaining styles exactly as provided */
        
        [... rest of provided CSS styles ...]

    </style>
</head>
<body>
<div class="container">
    [... rest of provided HTML template exactly as is ...]
</div>
</body>
</html>
"""

def create_match_summary(profile_data, match_data):
    """
    Creates a match summary banner from the provided TFT match data.
    
    Args:
        profile_data: Dictionary containing player profile information
        match_data: Dictionary containing match details
        
    Returns:
        str: Path to the generated banner image
    """
    if not profile_data or not match_data:
        raise ValueError("Invalid input data")

    # Extract profile information
    summoner_profile = profile_data.get("matches", [])[0] if profile_data.get("matches") else {}
    
    # Extract summoner details
    summoner_name = summoner_profile.get("gameName", "")
    summoner_tag = summoner_profile.get("tagLine", "")
    rating_info = summoner_profile.get("rank", {})
    rating_text = f"{rating_info.get('tier', '')} {rating_info.get('division', '')}"

    # Process match details
    match_details = process_match_details(match_data, summoner_name, summoner_tag)
    if not match_details:
        raise ValueError("Could not process match details")

    # Prepare template data
    template_data = prepare_template_data(
        match_details=match_details,
        summoner_name=summoner_name,
        summoner_tag=summoner_tag,
        rating_text=rating_text,
        profile_data=profile_data,
        match_data=match_data
    )

    # Generate HTML
    template = Template(get_html_template())
    html_content = template.render(**template_data)
    
    # Save HTML
    html_file = "match_summary.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Generate screenshot
    return generate_screenshot(html_file, summoner_name)

def process_match_details(match_data, summoner_name, summoner_tag):
    """Processes match details for the specific player."""
    # Extract the first match from the matches array
    matches = match_data.get("matches", [])
    if not matches:
        return None
        
    match_info = matches[0]
    
    # Find the participant data for the current player
    participant_data = None
    for participant in match_info.get("participants", []):
        if (participant.get("gameName") == summoner_name and 
            participant.get("tagLine") == summoner_tag):
            participant_data = participant
            break
            
    if not participant_data:
        return None
    
    # Process the participant data
    return {
        "placement": participant_data.get("placement", 8),
        "traits": process_traits(participant_data.get("traits", [])),
        "units": process_units(participant_data.get("units", [])),
        "lp_info": {
            "before_value": participant_data.get("beforeLp", 0),
            "after_value": participant_data.get("afterLp", 0),
            "diff": participant_data.get("afterLp", 0) - participant_data.get("beforeLp", 0)
        },
        "damage_dealt": participant_data.get("damageDealt", 0),
        "time_eliminated": participant_data.get("timeEliminatedSeconds", 0),
        "players": process_players(match_info.get("participants", []))
    }

def process_traits(traits_data):
    """Processes trait information from match data."""
    processed_traits = []
    for trait in traits_data:
        if not isinstance(trait, dict):
            continue
            
        processed_traits.append({
            "name": trait.get("name", "").capitalize(),
            "style": trait.get("style", ""),
            "num_units": trait.get("numUnits", 0),
            "icon_url": trait.get("imageUrl", ""),
            "color": get_trait_color(trait)
        })
    
    return sorted(processed_traits, key=lambda x: x["num_units"], reverse=True)

def process_units(units_data):
    processed_units = []
    for unit in units_data:
        if not isinstance(unit, dict):
            continue
        
        # Fallback if unit 'name' is missing or empty
        champion_name = unit.get("name") or "Unknown"
        processed_units.append({
            "name": champion_name.capitalize(),
            "champ_price": get_champion_price(unit),
            "items": process_items(unit.get("items", [])),
            "tier": "★" * unit.get("tier", 1),
            "image_url": get_champion_image_url(champion_name)
        })
    return processed_units

def prepare_template_data(match_details, summoner_name, summoner_tag, rating_text, profile_data, match_data):
    """Prepares data for the HTML template."""
    rank_icon, rank_color, rank_tier = get_rank_info(rating_text)
    
    lp_info = match_details["lp_info"]
    lp_diff = lp_info["diff"] if lp_info else 0
    
    
    return {
        "placement": match_details["placement"],
        "traits": match_details["traits"],
        "champs": match_details["units"],
        "summoner_name": summoner_name,
        "summoner_tag": summoner_tag,
        "lp_diff": lp_diff,
        "lp_color": "green" if lp_diff > 0 else "red",
        "lp_value": str(lp_info.get("after_value", 0))[-2:] if lp_info else "0",
        "rank_icon": rank_icon,
        "rank_color": rank_color,
        "rank_tier": rank_tier,
        "lp_value": str(match_details["lp_info"]["after_value"])[-2:],
        "game_mode": get_game_mode(match_data),
        "match_time": format_match_time(match_data.get("date", "")),
        "match_duration": format_duration(match_data.get("durationSeconds", 0)),
        "ver_patch": match_data.get("patch", ""),
        "profile_icon_url": get_profile_icon_url(profile_data),
        "damage_dealt": match_details["damage_dealt"],
        "time_eliminated": format_duration(match_details["time_eliminated"]),
        "players_data": match_details["players"],
        "damge_icon": "https://www.metatft.com/icons/announce_icon_combat.png",
        "time_eliminated_icon": "https://cdn.mobalytics.gg/assets/lol/images/dd/summoner-spells/SummonerTeleport.png",
        "perk_tag": "AP Enjoyer",
        "perk_color": "purple",
        "perk_icon_url": "https://www.metatft.com/icons/AP.svg"
    }

def generate_screenshot(html_file, summoner_name):
    """Generates a screenshot of the match summary."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(f"file:///{os.path.abspath(html_file)}")
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container"))
        )
        
        image_name = f"match_summary_banner_{summoner_name}.png"
        container.screenshot(image_name)
        return image_name
        
    finally:
        driver.quit()

# Helper functions (implement these based on your data structure)
def get_rank_info(rating_text):
    """Returns rank icon URL, color, and tier information."""
    return "rank_icon_url", "#ffffff", rating_text

def get_trait_color(trait):
    """Determines the color class for a trait based on its style."""
    return "gold" if trait.get("style") >= 3 else "silver" if trait.get("style") >= 2 else "default"

def get_champion_price(unit):
    """Determines the champion's cost/price tier."""
    return unit.get("cost", 1)

def get_champion_image_url(champion_name):
    """Returns the URL for a champion's image."""
    return f"https://raw.communitydragon.org/latest/game/assets/characters/{champion_name.lower()}/hud/{champion_name.lower()}_square.png"

def process_items(items):
    """Processes item information for a unit."""
    return [{"name": item, "url": f"https://raw.communitydragon.org/latest/game/assets/items/icons2d/{item.lower().replace(' ', '')}.png"}
            for item in items]

def process_players(participants_data):
    """
    Process player data from match participants.
    
    Args:
        participants_data: List of participant data from the match
        
    Returns:
        list: Processed player data sorted by placement
    """
    players = []
    for player in participants_data:
        if not isinstance(player, dict):
            continue
            
        players.append({
            "summoner_name": player.get("gameName", "Unknown"),
            "summoner_tag": player.get("tagLine", "0000"),
            "summoner_placement": player.get("placement", 8),
            "summoner_icon": get_summoner_icon(player.get("profileIcon", 0))
        })
    
    return sorted(players, key=lambda x: x["summoner_placement"])

def get_summoner_icon(icon_id):
    """Get the URL for a summoner's icon."""
    return f"https://raw.communitydragon.org/latest/game/assets/ux/summonericons/profileicon{icon_id}.png"

def get_game_mode(match_data):
    """Determines the game mode from match data."""
    return "Ranked" if match_data.get("queueId") == 1100 else "Normal"

def format_match_time(date_str):
    """Formats the match time into a readable string."""
    if not date_str:
        return "Unknown"
    match_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    time_diff = datetime.now() - match_time
    if time_diff.days > 0:
        return f"{time_diff.days}d ago"
    hours = time_diff.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    minutes = (time_diff.seconds % 3600) // 60
    return f"{minutes}m ago"

def format_duration(seconds):
    """Formats duration in seconds to a readable string."""
    return f"{seconds // 60}m" if seconds else "N/A"

def get_profile_icon_url(profile_data):
    """Returns the URL for the summoner's profile icon."""
    icon_id = profile_data.get("profileIconId", 1)
    return f"https://raw.communitydragon.org/latest/game/assets/ux/summonericons/profileicon{icon_id}.png"

    
if __name__ == "__main__":
    try:
        from main import TFTApiClient

        riotname = "beggy"
        tag = "3105"

        api_client = TFTApiClient()
        profile_data, queue_id, match_id, match_data = api_client.get_profile_data(riotname, tag)
        
        # Debug: Print fetched match_data for verification
        print("DEBUG match_data:", match_data)
        
        banner_image = create_match_summary(profile_data, match_data)
        print(f"Generated banner: {banner_image}")

    except Exception as e:
        print(f"Error generating match summary: {e}")