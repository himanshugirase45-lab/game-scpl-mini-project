"""
SCPL Simulation - Level Definitions
"""
LEVEL_CONFIG = {
    1: {
        "name": "First Shot",
        "attempts": 3,
        "target_distance_m": 12.0,
        "target_elevation_m": 0.0,
        "obstacles": [],
        "moving_target": False
    },
    2: {
        "name": "Long Range",
        "attempts": 3,
        "target_distance_m": 26.0,
        "target_elevation_m": 0.0,
        "obstacles": [
            {"type": "platform", "dist_m": 14.0, "elev_m": 0.5, "width_m": 4.0},
            {"type": "platform", "dist_m": 19.0, "elev_m": 0.8, "width_m": 3.0}
        ],
        "moving_target": False
    },
    3: {
        "name": "High Ground",
        "attempts": 3,
        "target_distance_m": 16.0,
        "target_elevation_m": 6.0,
        "obstacles": [
            {"type": "platform", "dist_m": 16.0, "elev_m": 6.0, "width_m": 4.0}
        ],
        "moving_target": False
    },
    4: {
        "name": "Wall Challenge",
        "attempts": 3,
        "target_distance_m": 19.0,
        "target_elevation_m": 0.0,
        "obstacles": [
            {"type": "wall", "dist_m": 11.0, "height_m": 6.5, "width_m": 0.8}
        ],
        "moving_target": False
    },
    5: {
        "name": "Moving Target",
        "attempts": 3,
        "target_distance_m": 22.0,
        "target_elevation_m": 0.0,
        "obstacles": [
            {"type": "wall", "dist_m": 15.0, "height_m": 4.0, "width_m": 0.5}
        ],
        "moving_target": True,
        "move_range_m": 4.0,
        "move_speed_m": 2.5
    }
}
