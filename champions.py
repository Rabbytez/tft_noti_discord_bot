import json

folder = "data"

with open(f"{folder}/TFT_13_lolchess_champions.json", "r") as f:
    data = json.load(f)
    
def get_champion_data(find_champion):
    for champion in data["champions"]:
        if champion["ingameKey"].lower() == find_champion.lower():
            return {
                "name": champion["name"],
                "icon": champion["imageUrl"],
                "cost": champion["cost"][0],
                "traits": champion["traits"],
            }
    return None

if __name__ == "__main__":
    
    find_champion = "TFT13_Ezreal"
    champion_info = get_champion_data(find_champion)
    if champion_info:
        print(json.dumps(champion_info, indent=4))
    else:
        print(f"Champion '{find_champion}' not found.")