import json

with open('moba_static_data.json',encoding='utf-8') as f:
    data = json.load(f)

def augment_data(augment_name):
    
    for i in data['data']['hextechAugments1']:
        # print(i['apiName'])
        if i['flatData']['slug'] == augment_name:
            augment_image_name=i['flatData']['imageSlug']
            url=f'https://cdn.mobalytics.gg/assets/tft/images/hextech-augments/set12/{augment_image_name}.webp?v=61'
            return url
    for i in data['data']['hextechAugments2']:
        # print(i['apiName'])
        if i['flatData']['slug'] == augment_name:
            augment_image_name=i['flatData']['imageSlug']
            url=f'https://cdn.mobalytics.gg/assets/tft/images/hextech-augments/set12/{augment_image_name}.webp?v=61'
            return url
    return False
# print()
# print(augment_data('TFT12_Augment_MultistrikerCrown'))
