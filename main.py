import requests
import json
import os
from datetime import datetime

def get_tft_profile(riot_id, tag, tft_set="TFTSet12", include_revival_matches=True):
    base_url = "https://api.metatft.com/public/profile/lookup_by_riotid"
    path = f"/TH2/{riot_id}/{tag}"
    params = {
        "source": "full_profile",
        "tft_set": tft_set,
        "include_revival_matches": str(include_revival_matches).lower()
    }
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.metatft.com",
        "Referer": "https://www.metatft.com/",
        "Sec-CH-UA": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }
    
    response = requests.get(f"{base_url}{path}", headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def save_json_to_file(data, folder_path, file_name):
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {file_path}")

def format_latest_match_for_discord(profile_data):
    matches = profile_data.get("matches", [])
    if not matches:
        return "No matches found."

    # Sort matches by timestamp to get the latest match
    latest_match = max(matches, key=lambda x: x["match_timestamp"])

    # Extract relevant data
    placement = latest_match.get("placement")
    match_id = latest_match.get("riot_match_id")
    avg_rating = latest_match.get("avg_rating")
    player_rating = latest_match["summary"].get("player_rating")
    total_damage = latest_match["summary"].get("total_damage_to_players")
    time_eliminated = latest_match["summary"].get("time_eliminated")
    last_round = latest_match["summary"].get("last_round")

    # Format the data into a template
    match_time = datetime.fromtimestamp(latest_match["match_timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
    template = (
        f"**Latest Match Summary**\n"
        f"Match ID: {match_id}\n"
        f"Placement: {placement}\n"
        f"Average Rating: {avg_rating}\n"
        f"Player Rating: {player_rating}\n"
        f"Total Damage to Players: {total_damage}\n"
        f"Time Eliminated: {time_eliminated} seconds\n"
        f"Last Round: {last_round}\n"
        f"Match Time: {match_time}\n"
    )
    return template

# Example usage
riot_id = "beggy"
tag = "3105"
profile_data = get_tft_profile(riot_id, tag)
save_json_to_file(profile_data, "output_folder", "profile_data.json")

# Get the latest match data formatted for Discord
discord_message = format_latest_match_for_discord(profile_data)
print(discord_message)