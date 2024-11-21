import requests
import json

folder = "outputs"

def get_profile_data(riotname, tag):
    
    file_name = f"TFT-13-profile-data-{riotname}-{tag}.json"
    url = "https://tft.dakgg.io"
    url_with_params = f"{url}/api/v1/summoners/th2/{riotname}-{tag}/matches?season=set13&page=1&queueId=0"
    
    headers = {
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

    response = requests.get(url_with_params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        match_id = data["matches"][0]["queueId"]
        print("200 profile Request successful!")
        print(f"Match ID: {match_id}")
        with open(f"{folder}/{file_name}", "w") as f:
            json.dump(data, f, indent=4)
        try:
            match_data = get_match_data(match_id,riotname,tag)
        except:
            print("Error getting match data")
        
    else:
        print(f"Request failed with status code: {response.status_code}")

    return data , match_id , match_data



def get_match_data(match_id,riotname,tag):
    
    file_name = f"TFT-13-match-data-{match_id}-{riotname}-{tag}.json"
    
    url = "https://tft.dakgg.io"
    url_with_params = f"{url}/api/v1/summoners/th2/{riotname}-{tag}/matches?season=set13&page=1&queueId={match_id}"

    headers = {
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
     
    response = requests.get(url_with_params, headers=headers)

    if response.status_code == 200:
        match_data = response.json()
        print("200 match Request successful!")
        with open(f"{folder}/{file_name}", "w") as f:
            json.dump(match_data, f, indent=4)

    else:
        print(f"Request failed with status code: {response.status_code}")


# Test the functions
if __name__ == "__main__":
    match_id = "42590337"
    riotname = "beggy"
    tag = "3105"
    profile_data = get_profile_data(riotname, tag)

