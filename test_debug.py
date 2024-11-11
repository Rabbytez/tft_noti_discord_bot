from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections.abc import Iterable
import time
import os
import json
import unittest

test_data = {
    'formatted_units': [],
    'summoner_name': 'TestPlayer',
    'summoner_tag': '123',
    'rank_tier': 'GOLD',
    'rank_division': 'I',
    'lp_value': 75,
    'lp_diff': 20,
    'placement': 3,
    'formatted_traits': [],
    'champions': []
}

def create_match_summary(profile_data):
    # Validate and prepare data
    formatted_units = profile_data.get('formatted_units', [])
    summoner_name = profile_data.get('summoner_name', '')
    summoner_tag = profile_data.get('summoner_tag', '')
    rank_tier = profile_data.get('rank_tier', '')
    rank_division = profile_data.get('rank_division', '')
    lp_value = profile_data.get('lp_value', 0)
    lp_diff = profile_data.get('lp_diff', 0)
    placement = profile_data.get('placement', 0)
    formatted_traits = profile_data.get('formatted_traits', [])
    champions = profile_data.get('champions', [])

    # Debug prints
    print("Data types of template variables:")
    print(f"formatted_units: {type(formatted_units)}")
    print(f"formatted_traits: {type(formatted_traits)}")
    print(f"champions: {type(champions)}")

    # Ensure lists are actually lists
    if not isinstance(formatted_units, list):
        formatted_units = list(formatted_units) if hasattr(formatted_units, '__iter__') else []
    if not isinstance(formatted_traits, list):
        formatted_traits = list(formatted_traits) if hasattr(formatted_traits, '__iter__') else []
    if not isinstance(champions, list):
        champions = list(champions) if hasattr(champions, '__iter__') else []

    # HTML template (your existing template)
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Match Summary</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #1c1c1e; color: #f7f7f7; }
            .summary { border: 1px solid #ccc; padding: 20px; margin: 20px; background-color: #2c2f33; }
            .title { font-size: 24px; font-weight: bold; margin-bottom: 10px; color: #ffd700; }
            .info { font-size: 18px; margin: 5px 0; }
            .traits, .units, .champion-list { margin-top: 10px; }
            .unit-item { margin: 5px 0; }
            .rank { font-weight: bold; color: #4caf50; }
            .champion-item { display: inline-block; margin: 5px; }
            .champion-icon img { width: 50px; height: 50px; }
        </style>
    </head>
    <body>
        <div class="summary">
            <div class="title">Match Summary</div>
            <div class="info">Summoner: {{ summoner_name }}#{{ summoner_tag }}</div>
            <div class="info">Rank: <span class="rank">{{ rank_tier }} {{ rank_division }}</span> ({{ lp_value }} LP)</div>
            <div class="info">LP Change: {{ lp_diff }}</div>
            <div class="info">Placement: {{ placement }}</div>

            <div class="traits">
                <div class="title">Traits</div>
                <ul>
                    {% for trait in formatted_traits %}
                    <li>{{ trait }}</li>
                    {% endfor %}
                </ul>
            </div>

            <div class="units">
                <div class="title">Units</div>
                <ul>
                    {% for unit in formatted_units %}
                    <li class="unit-item">
                        <strong>{{ unit.name }}</strong> (Tier: {{ unit.tier }})<br>
                        Items: 
                        {% if unit.items %}
                            <ul>
                                {% for item in unit.items %}
                                    <li>
                                        <img src="{{ item.url }}" alt="{{ item.name }}" style="width: 30px; height: 30px;"> 
                                        {{ item.name }}
                                    </li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            None
                        {% endif %}
                    </li>
                    {% endfor %}
                </ul>
            </div>

                        
            <div class="champion-list">
                <div class="title">Champions</div>
                {% for champion in champions %}
                <div class="champion-item">
                    <div class="champion-icon price-{{ champion.price }}">
                        <img src="{{ champion.icon }}" alt="Champion Icon" onerror="this.onerror=null; this.src='https://via.placeholder.com/50';">
                    </div>
                    <div class="champion-stars">{{ champion.stars }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """
    
        # Render the HTML with Jinja2
    template = Template(html_template)
    try:
        rendered_html = template.render(
            formatted_units=formatted_units,
            summoner_name=summoner_name,
            summoner_tag=summoner_tag,
            rank_tier=rank_tier,
            rank_division=rank_division,
            lp_value=lp_value,
            lp_diff=lp_diff,
            placement=placement,
            formatted_traits=formatted_traits,
            champions=champions
        )
        
        # Create 'outputs' folder if it does not exist
        output_folder = "outputs"
        os.makedirs(output_folder, exist_ok=True)

        # Save HTML to the outputs folder
        html_path = os.path.join(output_folder, "match_summary.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
            
        return html_path
        
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        print(f"Data causing error:")
        print(f"formatted_units: {formatted_units}")
        print(f"formatted_traits: {formatted_traits}")
        print(f"champions: {champions}")
        raise

html_path = create_match_summary(test_data)
print(f"Generated HTML file at: {html_path}")

class TestMatchSummary(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            'formatted_units': [
                {'name': 'Unit1', 'tier': 1, 'items': [{'url': 'item1.png', 'name': 'Item1'}]},
                {'name': 'Unit2', 'tier': 2, 'items': []}
            ],
            'summoner_name': 'TestPlayer',
            'summoner_tag': '123',
            'rank_tier': 'GOLD',
            'rank_division': 'I',
            'lp_value': 75,
            'lp_diff': 20,
            'placement': 3,
            'formatted_traits': ['Trait1', 'Trait2'],
            'champions': [
                {'name': 'Champ1', 'price': 1, 'icon': 'icon1.png', 'stars': '★★★'},
                {'name': 'Champ2', 'price': 2, 'icon': 'icon2.png', 'stars': '★★'}
            ]
        }
        
        # Ensure output directory exists
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def tearDown(self):
        # Clean up test files
        try:
            os.remove(os.path.join(self.output_dir, "match_summary.html"))
        except FileNotFoundError:
            pass

    def test_valid_input(self):
        """Test with valid input data"""
        html_path = create_match_summary(self.test_data)
        self.assertTrue(os.path.exists(html_path))
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(self.test_data['summoner_name'], content)
            self.assertIn(self.test_data['rank_tier'], content)

    def test_missing_data(self):
        """Test with missing data fields"""
        minimal_data = {'summoner_name': 'Player'}
        html_path = create_match_summary(minimal_data)
        self.assertTrue(os.path.exists(html_path))

    def test_empty_lists(self):
        """Test with empty lists"""
        empty_data = self.test_data.copy()
        empty_data['formatted_units'] = []
        empty_data['formatted_traits'] = []
        empty_data['champions'] = []
        html_path = create_match_summary(empty_data)
        self.assertTrue(os.path.exists(html_path))

    def test_invalid_types(self):
        """Test with invalid data types"""
        invalid_data = self.test_data.copy()
        invalid_data['formatted_units'] = "not a list"
        invalid_data['lp_value'] = "not a number"
        with self.assertRaises(Exception):
            create_match_summary(invalid_data)

if __name__ == '__main__':
    unittest.main()