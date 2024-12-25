import os
import requests
import json
from typing import Tuple, Dict, Optional
from datetime import datetime

class TFTApiClient:
    def __init__(self, base_url: str = "https://tft.dakgg.io", output_folder: str = "outputs"):
        self.base_url = base_url
        self.output_folder = output_folder
        self.headers = {
            "Content-Type": "application/json",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "priority": "u=1, i",
            "origin": "https://lolchess.gg",
            "referer": "https://lolchess.gg/",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
        }
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

    def _make_request(self, url: str) -> Optional[dict]:
        """Make HTTP request with error handling and logging."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def _save_response(self, data: dict, filename: str) -> None:
        """Save API response to file with error handling."""
        try:
            filepath = os.path.join(self.output_folder, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"Data saved to {filepath}")
        except IOError as e:
            print(f"Failed to save data: {e}")

    def get_profile_data(self, riotname: str, tag: str, season: str = "set13", page: int = 1, queue_id: int = 0) -> Tuple[Optional[dict], Optional[int], Optional[str], Optional[dict]]:
        """
        Fetch profile data and latest match information.
        
        Returns:
            Tuple containing (profile_data, queue_id, match_id, match_data)
        """
        profile_endpoint = f"/api/v1/summoners/th2/{riotname}-{tag}/matches"
        url = f"{self.base_url}{profile_endpoint}?season={season}&page={page}&queueId={queue_id}"
        
        data = self._make_request(url)
        if not data:
            return None, None, None, None

        # Save profile data
        profile_filename = f"TFT-13-profile-data-{riotname}-{tag}.json"
        self._save_response(data, profile_filename)

        # Extract match information
        try:
            first_match = data["matches"][0]
            match_id = first_match["matchId"]
            queue_id = first_match["queueId"]
            
            # Get match details
            match_data = self.get_match_data(queue_id, match_id, riotname, tag)
            
            print(f"Successfully retrieved profile data and match information:")
            print(f"Queue ID: {queue_id}")
            print(f"Match ID: {match_id}")
            
            return data, queue_id, match_id, match_data
            
        except (KeyError, IndexError) as e:
            print(f"Failed to process profile data: {e}")
            return data, None, None, None

    def get_match_data(self, queue_id: int, match_id: str, riotname: str, tag: str, season: str = "set13", page: int = 1) -> Optional[dict]:
        """
        Fetch detailed match data for a specific match.
        """
        match_endpoint = f"/api/v1/summoners/th2/{riotname}-{tag}/matches"
        url = f"{self.base_url}{match_endpoint}?season={season}&page={page}&queueId={queue_id}"
        
        match_data = self._make_request(url)
        if not match_data:
            return None

        # Save match data
        match_filename = f"TFT-13-match-data-{match_id}-{riotname}-{tag}.json"
        self._save_response(match_data, match_filename)
        
        return match_data

def main():
    # Example usage
    riotname = "beggy"
    tag = "3105"
    
    api_client = TFTApiClient()
    profile_data, queue_id, match_id, match_data = api_client.get_profile_data(riotname, tag)
    
    if profile_data:
        print("Data retrieval successful")
    else:
        print("Failed to retrieve data")

if __name__ == "__main__":
    main()