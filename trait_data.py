import requests
import svgutils.transform as sg
import json
import re
import os
import cairosvg

# Load the traits data from 'traits.json'
with open('traits.json', encoding='utf-8') as f:
    augments = json.load(f)

# check dir
if not os.path.exists('traits'):
    os.makedirs('traits')


def parse_dimension(value):
    # Function to parse dimension strings like '200px' to float values
    return float(re.sub(r'[^\d\.]', '', value))


def merge_background(trait_url, background_url, trait_name, trait_num):
    # Download SVG content from the URLs
    bg_response = requests.get(background_url)
    icon_response = requests.get(trait_url)

    # Save SVG content to files
    with open('traits/background.svg', 'wb') as f:
        f.write(bg_response.content)

    with open('traits/icon.svg', 'wb') as f:
        f.write(icon_response.content)

    # Load SVG files
    background_svg = sg.fromfile('traits/background.svg')
    icon_svg = sg.fromfile('traits/icon.svg')

    # Get root elements
    bg_root = background_svg.getroot()
    icon_root = icon_svg.getroot()

    # Get sizes of background SVG
    bg_width_raw = background_svg.width
    bg_height_raw = background_svg.height
    bg_width = parse_dimension(bg_width_raw)
    bg_height = parse_dimension(bg_height_raw)

    # Get sizes of icon SVG
    icon_width_raw = icon_svg.width
    icon_height_raw = icon_svg.height
    icon_width = parse_dimension(icon_width_raw)
    icon_height = parse_dimension(icon_height_raw)

    # Desired background width
    desired_bg_width = 150  # You can set this to any desired width

    # Calculate scaling factor for the background
    scaling_factor = desired_bg_width / bg_width

    # Scale the background root element
    bg_root.scale(scaling_factor)

    desired_icon_width=58
    scaling_factor_icon = desired_icon_width / icon_width
    icon_root.scale(scaling_factor_icon)

    bg_width = 150
    bg_height = 150
    icon_height=58
    icon_width=58
    # Calculate offsets to center the icon over the background
    x_offset = (bg_width - icon_width) / 2
    y_offset = (bg_height - icon_height) / 2

    # Move icon to the calculated position
    icon_root.moveto(x_offset, y_offset)

    fig = sg.SVGFigure(f"{bg_width}", f"{bg_height}")

    # Append background and icon to the figure
    fig.append([bg_root, icon_root])

    # Save the merged SVG to a file

    output_filename = f'traits/{trait_name}_{trait_num}.svg'

    fig.save(output_filename)


    output_filename_png = f'traits/{trait_name}_{trait_num}.png'
    # Convert SVG to PNG
    cairosvg.svg2png(url=output_filename, write_to=output_filename_png, parent_height=bg_height, parent_width=bg_width,output_height=150,output_width=150)
    # Optionally, return the path to the merged SVG
    return output_filename_png


def trait_data(trait):
    # Extract trait number and trait name
    trait_num = trait["numUnits"]
    trait_name = trait["slug"]

    for i in augments['traits']:
        if i['key'].lower() == trait_name.lower():
            trait_url = i['blackImageUrl']
            trait_url = 'https:' + trait_url
            if len(i['styles']) == 1:
                background_url = 'https://cdn.dak.gg/tft/images2/tft/traits/background/unique.svg'
            else:
                # Ensure trait_num is within the valid range
                if 1 <= int(trait_num) <= len(i['styles']):
                    background_name = i['styles'][int(trait_num) - 1]['style']

                    if background_name == 'bronze':
                        background_url = 'https://cdn.dak.gg/tft/images2/tft/traits/background/bronze.svg'
                    elif background_name == 'silver':
                        background_url = 'https://cdn.dak.gg/tft/images2/tft/traits/background/silver.svg'
                    elif background_name == 'gold':
                        background_url = 'https://cdn.dak.gg/tft/images2/tft/traits/background/gold.svg'
                    elif background_name == 'chromatic':
                        background_url = 'https://cdn.dak.gg/tft/images2/tft/traits/background/chromatic.svg'
                else:
                    # Handle the case where trait_num is out of range
                    background_url = 'https://cdn.dak.gg/tft/images2/tft/traits/background/default.svg'

            return merge_background(trait_url, background_url, trait_name, trait_num)


def get_trait_img(latest_match):
    latest_match_traits = []
    participants = latest_match.get("data", {}).get("tft", {}).get("matchV2", {}).get("participants", {})
    traits_list = participants[0].get("traits", {})

    for i in traits_list:
        trait = trait_data(i)
        latest_match_traits.append(trait)

    return latest_match_traits


if __name__ == "__main__":
    # pip install svgutils

    import main
    match_id = "42590337"
    riotname = "beggy"
    tag = "3105"
    match_data = main.get_match_data(match_id,riotname,tag)

    print(get_trait_img(match_data))
