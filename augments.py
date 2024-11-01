import json

with open('TFTSet12_latest_en_us.json',encoding='utf-8') as f:
    augments = json.load(f)

def augment_data(augment_name):
    
    for i in augments['augments']:
        # print(i['apiName'])
        if i['apiName'] == augment_name:
            # "icon": "ASSETS/Maps/TFT/Icons/Augments/Hexcore/All-that-Shimmers-II.tex",
            # augement = all-that-shimmers-ii
            augement_path=i['icon'].split('/')[-1].split('.')[0]
            augement_path=augement_path.lower()
            # https://cdn.metatft.com/cdn-cgi/image/width=46,height=46,format=auto/https://cdn.metatft.com/file/metatft/augments/little-buddies-ii.png
            url=f"https://cdn.metatft.com/cdn-cgi/image/width=46,height=46,format=auto/https://cdn.metatft.com/file/metatft/augments/{augement_path}.png"
            return url
    return False
# print()
# print(augment_data('TFT12_Augment_MultistrikerCrown'))