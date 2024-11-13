
def get_champion_assets():
    
    champion_assets = {
            "Ashe": {
                "url": "https://rerollcdn.com/characters/Skin/12/Ashe.png",
                "price": 1,
            },
            "Blitzcrank": {
                "url": "https://rerollcdn.com/characters/Skin/12/Blitzcrank.png",
                "price": 1,
            },
            "Elise": {
                "url": "https://rerollcdn.com/characters/Skin/12/Elise.png",
                "price": 1,
            },
            "Jax": {"url": "https://rerollcdn.com/characters/Skin/12/Jax.png", "price": 1},
            "Jayce": {
                "url": "https://rerollcdn.com/characters/Skin/12/Jayce.png",
                "price": 1,
            },
            "Lillia": {
                "url": "https://rerollcdn.com/characters/Skin/12/Lillia.png",
                "price": 1,
            },
            "Nomsy": {
                "url": "https://rerollcdn.com/characters/Skin/12/Nomsy.png",
                "price": 1,
            },
            "Poppy": {
                "url": "https://rerollcdn.com/characters/Skin/12/Poppy.png",
                "price": 1,
            },
            "Seraphine": {
                "url": "https://rerollcdn.com/characters/Skin/12/Seraphine.png",
                "price": 1,
            },
            "Soraka": {
                "url": "https://rerollcdn.com/characters/Skin/12/Soraka.png",
                "price": 1,
            },
            "Twitch": {
                "url": "https://rerollcdn.com/characters/Skin/12/Twitch.png",
                "price": 1,
            },
            "Warwick": {
                "url": "https://rerollcdn.com/characters/Skin/12/Warwick.png",
                "price": 1,
            },
            "Ziggs": {
                "url": "https://rerollcdn.com/characters/Skin/12/Ziggs.png",
                "price": 1,
            },
            "Zoe": {"url": "https://rerollcdn.com/characters/Skin/12/Zoe.png", "price": 1},
            "Ahri": {
                "url": "https://rerollcdn.com/characters/Skin/12/Ahri.png",
                "price": 2,
            },
            "Akali": {
                "url": "https://rerollcdn.com/characters/Skin/12/Akali.png",
                "price": 2,
            },
            "Cassiopeia": {
                "url": "https://rerollcdn.com/characters/Skin/12/Cassiopeia.png",
                "price": 2,
            },
            "Galio": {
                "url": "https://rerollcdn.com/characters/Skin/12/Galio.png",
                "price": 2,
            },
            "Kassadin": {
                "url": "https://rerollcdn.com/characters/Skin/12/Kassadin.png",
                "price": 2,
            },
            "KogMaw": {
                "url": "https://rerollcdn.com/characters/Skin/12/KogMaw.png",
                "price": 2,
            },
            "Nilah": {
                "url": "https://rerollcdn.com/characters/Skin/12/Nilah.png",
                "price": 2,
            },
            "Nunu": {
                "url": "https://rerollcdn.com/characters/Skin/12/Nunu.png",
                "price": 2,
            },
            "Rumble": {
                "url": "https://rerollcdn.com/characters/Skin/12/Rumble.png",
                "price": 2,
            },
            "Shyvana": {
                "url": "https://rerollcdn.com/characters/Skin/12/Shyvana.png",
                "price": 2,
            },
            "Syndra": {
                "url": "https://rerollcdn.com/characters/Skin/12/Syndra.png",
                "price": 2,
            },
            "Tristana": {
                "url": "https://rerollcdn.com/characters/Skin/12/Tristana.png",
                "price": 2,
            },
            "Zilean": {
                "url": "https://rerollcdn.com/characters/Skin/12/Zilean.png",
                "price": 2,
            },
            "Bard": {
                "url": "https://rerollcdn.com/characters/Skin/12/Bard.png",
                "price": 3,
            },
            "Ezreal": {
                "url": "https://rerollcdn.com/characters/Skin/12/Ezreal.png",
                "price": 3,
            },
            "Hecarim": {
                "url": "https://rerollcdn.com/characters/Skin/12/Hecarim.png",
                "price": 3,
            },
            "Hwei": {
                "url": "https://rerollcdn.com/characters/Skin/12/Hwei.png",
                "price": 3,
            },
            "Jinx": {
                "url": "https://rerollcdn.com/characters/Skin/12/Jinx.png",
                "price": 3,
            },
            "Katarina": {
                "url": "https://rerollcdn.com/characters/Skin/12/Katarina.png",
                "price": 3,
            },
            "Mordekaiser": {
                "url": "https://rerollcdn.com/characters/Skin/12/Mordekaiser.png",
                "price": 3,
            },
            "Neeko": {
                "url": "https://rerollcdn.com/characters/Skin/12/Neeko.png",
                "price": 3,
            },
            "Shen": {
                "url": "https://rerollcdn.com/characters/Skin/12/Shen.png",
                "price": 3,
            },
            "Swain": {
                "url": "https://rerollcdn.com/characters/Skin/12/Swain.png",
                "price": 3,
            },
            "Veigar": {
                "url": "https://rerollcdn.com/characters/Skin/12/Veigar.png",
                "price": 3,
            },
            "Vex": {"url": "https://rerollcdn.com/characters/Skin/12/Vex.png", "price": 3},
            "Wukong": {
                "url": "https://rerollcdn.com/characters/Skin/12/Wukong.png",
                "price": 3,
            },
            "Fiora": {
                "url": "https://rerollcdn.com/characters/Skin/12/Fiora.png",
                "price": 4,
            },
            "Gwen": {
                "url": "https://rerollcdn.com/characters/Skin/12/Gwen.png",
                "price": 4,
            },
            "Kalista": {
                "url": "https://rerollcdn.com/characters/Skin/12/Kalista.png",
                "price": 4,
            },
            "Karma": {
                "url": "https://rerollcdn.com/characters/Skin/12/Karma.png",
                "price": 4,
            },
            "Nami": {
                "url": "https://rerollcdn.com/characters/Skin/12/Nami.png",
                "price": 4,
            },
            "Nasus": {
                "url": "https://rerollcdn.com/characters/Skin/12/Nasus.png",
                "price": 4,
            },
            "Olaf": {
                "url": "https://rerollcdn.com/characters/Skin/12/Olaf.png",
                "price": 4,
            },
            "Rakan": {
                "url": "https://rerollcdn.com/characters/Skin/12/Rakan.png",
                "price": 4,
            },
            "Ryze": {
                "url": "https://rerollcdn.com/characters/Skin/12/Ryze.png",
                "price": 4,
            },
            "TahmKench": {
                "url": "https://rerollcdn.com/characters/Skin/12/TahmKench.png",
                "price": 4,
            },
            "Taric": {
                "url": "https://rerollcdn.com/characters/Skin/12/Taric.png",
                "price": 4,
            },
            "Varus": {
                "url": "https://rerollcdn.com/characters/Skin/12/Varus.png",
                "price": 4,
            },
            "Briar": {
                "url": "https://rerollcdn.com/characters/Skin/12/Briar.png",
                "price": 5,
            },
            "Camille": {
                "url": "https://rerollcdn.com/characters/Skin/12/Camille.png",
                "price": 5,
            },
            "Diana": {
                "url": "https://rerollcdn.com/characters/Skin/12/Diana.png",
                "price": 5,
            },
            "Milio": {
                "url": "https://rerollcdn.com/characters/Skin/12/Milio.png",
                "price": 5,
            },
            "Morgana": {
                "url": "https://rerollcdn.com/characters/Skin/12/Morgana.png",
                "price": 5,
            },
            "Norra": {
                "url": "https://cdn.metatft.com/cdn-cgi/image/width=48,height=48,format=auto/https://cdn.metatft.com/file/metatft/champions/tft12_norra.png",
                "price": 5,
            },
            "Norra-and-yuumi": {
                "url": "https://cdn.metatft.com/cdn-cgi/image/width=48,height=48,format=auto/https://cdn.metatft.com/file/metatft/champions/tft12_norra.png",
                "price": 5,
            },
            "Yuumi": {
                "url": "https://cdn.metatft.com/cdn-cgi/image/width=48,height=48,format=auto/https://cdn.metatft.com/file/metatft/champions/tft12_yuumi.png",
                "price": 5,
            },
            "Smolder": {
                "url": "https://rerollcdn.com/characters/Skin/12/Smolder.png",
                "price": 5,
            },
            "Xerath": {
                "url": "https://rerollcdn.com/characters/Skin/12/Xerath.png",
                "price": 5,
            },
        }
    
    return champion_assets

def get_rank_assets():
    
    rank_data = {
    "Iron": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/iron.png",
        "color": "#6d6d6d",  # Grey for Iron
    },
    "Bronze": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/bronze.png",
        "color": "#cd7f32",  # Bronze color
    },
    "Silver": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/silver.png",
        "color": "#c0c0c0",  # Silver color
    },
    "Gold": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/gold.png",
        "color": "#ffd700",  # Gold color
    },
    "Platinum": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/platinum.png",
        "color": "#00ff00",  # Green for Platinum
    },
    "Emerald": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/emerald.png",
        "color": "#2ecc71",  # Emerald green
    },
    "Diamond": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/diamond.png",
        "color": "#00c8ff",  # Blue for Diamond
    },
    "Master": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/master.png",
        "color": "#ff00ff",  # Purple for Master
    },
    "GrandMaster": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/grandmaster.png",
        "color": "#ff4500",  # Red-orange for GrandMaster
    },
    "Challenger": {
        "icon": "https://cdn.metatft.com/file/metatft/ranks/challenger.png",
        "color": "#ff6347",  # Tomato color for Challenger
    },
}
        
    return rank_data

def get_trait_data():
        
    trait_data = {
        "frost": {
            "3": "silver",
            "6": "gold",
            "9": "prismatic",
        },
        "arcana": {
            "2": "silver",
            "3": "gold",
            "4": "gold",
            "5": "gold",
        },
        "chrono": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
        },
        "dragon": {
            "2": "silver",
            "3": "gold",
        },
        "druid": {
            "1": "silver",
        },
        "eldritch": {
            "3": "silver",
            "5": "silver",
            "7": "gold",
            "10": "prismatic",
        },
        "faerie": {
            "3": "silver",
            "5": "silver",
            "7": "gold",
            "9": "gold",
        },
        "honeymancy": {
            "3": "silver",
            "5": "gold",
            "7": "gold",
        },
        "portal": {
            "3": "silver",
            "6": "gold",
            "8": "gold",
            "10": "prismatic",
        },
        "pyro": {
            "2": "silver",
            "3": "silver",
            "4": "gold",
            "5": "gold",
        },
        "sugarcraft": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
            "8": "gold",
        },
        "witchcraft": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
            "8": "gold",
        },
        "explorer": {
            "1": "copper",
        },
        "ascendant": {
            "1": "copper",
        },
        "bastion": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
            "8": "gold",
        },
        "batqueen": {
            "1": "copper",
        },
        "bestfriends": {
            "1": "copper",
        },
        "blaster": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
        },
        "hunter": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
        },
        "incantor": {
            "2": "silver",
            "4": "gold",
        },
        "mage": {
            "3": "silver",
            "5": "gold",
            "7": "gold",
            "10": "prismatic",
        },
        "multistriker": {
            "3": "silver",
            "5": "gold",
            "7": "gold",
            "9": "gold",  
        },
        "preserver": {
            "2": "silver",
            "3": "gold",
            "4": "gold",
            "5": "gold",
        },
        "scholar": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
        },
        "shapeshifter": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
            "8": "gold",
        },
        "vanguard": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
        },
        "warrior": {
            "2": "silver",
            "4": "gold",
            "6": "gold",
        },
    }

    return trait_data