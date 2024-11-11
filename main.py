import requests
import json
import os
from create_match_summary import create_match_summary
from show_match_detail import show_match_detail
from match_rounds_report import generate_match_rounds_report

folder_path = "outputs/"

def get_tft_profile(riot_id, tag, tft_set="TFTSet12", include_revival_matches=False):
    base_url = "https://api.metatft.com/public/profile/lookup_by_riotid"
    path = f"/TH2/{riot_id}/{tag}"
    params = {
        "source": "full_profile",
        "tft_set": tft_set,
        "include_revival_matches": str(include_revival_matches).lower(),
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.metatft.com",
        "Referer": "https://www.metatft.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }
    refresh_url = f"https://api.metatft.com/public/profile/refresh_by_riotid/TH2/{riot_id}/{tag}?tier=1"
    requests.post(f"{refresh_url}", headers=headers)

    response = requests.get(f"{base_url}{path}", headers=headers, params=params)

    if response.status_code == 200:
        try:
            data = response.json()  # Parse JSON here
        except json.JSONDecodeError:
            print("Failed to parse JSON from response.")
            return None
        save_json_to_file(data, folder_path, f"{riot_id}_{tag}_profile.json")
        return data
    else:
        response.raise_for_status()

def save_json_to_file(data, folder_path, file_name):
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    # Place any testing or standalone code here
    riot_id = "beggy"
    tag = "3105"
    profile_data = get_tft_profile(riot_id, tag)

