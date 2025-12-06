import requests
import json

def get_puuid_by_riot_id(game_name, tag_line, region="asia"):
    """Get PUUID from Riot ID using Riot API"""
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get("puuid")
    else:
        print(f"Failed to get PUUID: {response.status_code}")
        return None

def get_match_ids_by_puuid(puuid, region="sea", count=20):
    """Get match IDs for a player using Riot API"""
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get match IDs: {response.status_code}")
        return []

def get_riot_match_data(match_id, region="sea"):
    """Get match data from Riot API"""
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get match data: {response.status_code}")
        return None

if __name__ == "__main__":
    # Test with sabree3#3105
    print("Testing Riot API...")
    puuid = get_puuid_by_riot_id("sabree3", "3105")
    if puuid:
        print(f"PUUID: {puuid}")
        match_ids = get_match_ids_by_puuid(puuid)
        print(f"Found {len(match_ids)} matches")
        if match_ids:
            print(f"Latest match ID: {match_ids[0]}")

            # Get match data
            match_data = get_riot_match_data(match_ids[0])
            if match_data:
                print(f"Match data keys: {match_data.keys()}")
                print(f"Match info: {match_data['info'].keys()}")
