import json

folder = "data"

with open(f"{folder}/TFT_13_lolchess_items_11202024.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def get_item_data(find_item):
    for item in data["items"]:
        if item["ingameKey"].lower() == find_item.lower():
            return {
                "name": item["ingameKey"],
                "icon": item["imageUrl"],
                "description": item["desc"],
                "stats": item["fromDesc"],
            }
    return None

if __name__ == "__main__":
    find_item = "TFT_Item_AdaptiveHelm"
    item_info = get_item_data(find_item)
    if item_info:
        print(json.dumps(item_info, indent=4))
    else:
        print(f"Item '{find_item}' not found.")