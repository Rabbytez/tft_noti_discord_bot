import json

folder = "data"

with open(f"{folder}/TFT_13_lolchess_traits_11202024.json", "r") as f:
    data = json.load(f)

def get_trait_data(find_trait):
    for trait in data["traits"]:
        if trait["ingameKey"].lower() == find_trait.lower():
            return {
                "name": trait["name"],
                "icon": trait["imageUrl"],
                "description": trait["desc"],
                "stat": trait["stats"],
                "style": trait["styles"],
            }
    return None

if __name__ == "__main__":
    find_trait = "TFT13_Cabal"
    trait_info = get_trait_data(find_trait)
    if trait_info:
        print(json.dumps(trait_info, indent=4))
    else:
        print(f"Trait '{find_trait}' not found.")