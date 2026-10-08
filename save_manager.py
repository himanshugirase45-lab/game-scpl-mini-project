import os
import json

SAVE_FILE = 'save_data.json'

def default_save():
    return {
        'levels': {
            '1': {'unlocked': True, 'score': 0, 'stars': 0},
            '2': {'unlocked': False, 'score': 0, 'stars': 0},
            '3': {'unlocked': False, 'score': 0, 'stars': 0},
            '4': {'unlocked': False, 'score': 0, 'stars': 0},
            '5': {'unlocked': False, 'score': 0, 'stars': 0}
        },
        'settings': {
            'volume': 1.0,
            'mute': False,
            'fullscreen': False
        }
    }

def load_save():
    if not os.path.exists(SAVE_FILE):
        save_data(default_save())
        return default_save()
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            # Basic validation
            if 'levels' not in data or 'settings' not in data:
                return default_save()
            return data
    except (json.JSONDecodeError, IOError):
        return default_save()

def save_data(data):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError:
        print("Failed to save progress.")

def unlock_level(level_id):
    data = load_save()
    if str(level_id) in data['levels']:
        data['levels'][str(level_id)]['unlocked'] = True
    save_data(data)

def update_score(level_id, score, stars):
    data = load_save()
    lid = str(level_id)
    if lid in data['levels']:
        if score > data['levels'][lid]['score']:
            data['levels'][lid]['score'] = score
        if stars > data['levels'][lid]['stars']:
            data['levels'][lid]['stars'] = stars
    save_data(data)

def update_settings(volume, mute, fullscreen):
    data = load_save()
    data['settings'] = {
        'volume': volume,
        'mute': mute,
        'fullscreen': fullscreen
    }
    save_data(data)
