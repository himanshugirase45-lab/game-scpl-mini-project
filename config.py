"""
SCPL Simulation - Configuration & Constants
Defines screen dimensions, colors, physics parameters, and default values.
"""
import pygame

# Screen Settings
WIDTH = 1280
HEIGHT = 720
FPS = 60

# Physical Unit Scaling
# 1 meter = 50 pixels (e.g. 10 meters = 500 pixels)
PIXELS_PER_METER = 50.0

# Default Physics Parameters
DEFAULT_GRAVITY = 9.8            # m/s^2 (Standard Earth gravity)
DEFAULT_BALL_ELASTICITY = 0.75   # Coefficient of restitution for ball (0.0 to 1.0)
DEFAULT_GROUND_ELASTICITY = 0.50 # Ground bounciness
DEFAULT_STICKMAN_ELASTICITY = 0.40 # Target bounciness
DEFAULT_BALL_MASS = 1.0          # kg
DEFAULT_BALL_RADIUS = 16         # pixels (~0.32 meters)

# Ground Y
GROUND_Y = HEIGHT - 90           # Y-coordinate of ground surface (630)

# Slingshot / Bow Defaults (Elevation measured upwards from ground)
DEFAULT_BOW_X = 220
DEFAULT_BOW_ELEVATION_M = 3.8    # Elevation in meters
MIN_BOW_ELEVATION_M = 0.2        # Min elevation in meters (near ground)
INITIAL_MAX_BOW_ELEVATION_M = 30.0 # Initial slider max (dynamically unbounded)
DEFAULT_BOW_ELEVATION = int(DEFAULT_BOW_ELEVATION_M * PIXELS_PER_METER) # 190 px
MIN_BOW_ELEVATION = int(MIN_BOW_ELEVATION_M * PIXELS_PER_METER)         # 10 px
DEFAULT_BOW_HEIGHT = GROUND_Y - DEFAULT_BOW_ELEVATION
SLING_MAX_PULL = 150
LAUNCH_POWER_MULTIPLIER = 8.5    # Velocity scale per pixel of stretch

# Target (Stick Figure) Defaults (Distance in meters from bow)
DEFAULT_STICKMAN_DISTANCE_M = 14.0 # meters
MIN_STICKMAN_DISTANCE_M = 1.0      # meters (close up)
INITIAL_MAX_STICKMAN_DISTANCE_M = 50.0 # Initial slider max (dynamically unbounded)
DEFAULT_STICKMAN_DISTANCE = int(DEFAULT_STICKMAN_DISTANCE_M * PIXELS_PER_METER) # 700 px
MIN_STICKMAN_DISTANCE = int(MIN_STICKMAN_DISTANCE_M * PIXELS_PER_METER)

# Physics Sub-stepping
PHYSICS_STEPS = 10

# Collision Types for Pymunk
COLLISION_BALL = 1
COLLISION_STICKMAN = 2
COLLISION_GROUND = 3
COLLISION_WALL = 4

# Sleek Dark Theme Color Palette
COLOR_BG_DARK_TOP = (12, 16, 24)
COLOR_BG_DARK_BOTTOM = (22, 28, 40)
COLOR_GROUND_BASE = (26, 32, 44)
COLOR_GROUND_ACCENT = (42, 54, 76)
COLOR_GROUND_LINE = (0, 200, 255) # Subtle neon edge

COLOR_FENCE_WOOD = (55, 48, 42)
COLOR_FENCE_HIGHLIGHT = (80, 70, 62)
COLOR_FENCE_SHADOW = (32, 28, 24)

# Object Colors
COLOR_BALL_RED = (235, 45, 45)
COLOR_BALL_SHINE = (255, 140, 140)
COLOR_BALL_SHADOW = (160, 20, 20)
COLOR_BALL_TRAIL = (255, 80, 80)

COLOR_STICKMAN = (250, 250, 255)
COLOR_STICKMAN_HIT = (255, 100, 100)

COLOR_BOW_WOOD = (100, 65, 40)
COLOR_BOW_DARK = (60, 38, 22)
COLOR_BOW_STRING = (210, 190, 160)
COLOR_BOW_POUCH = (130, 80, 45)

# UI & HUD Colors
COLOR_WHITE = (255, 255, 255)
COLOR_MUTED = (160, 175, 195)
COLOR_CARD_BG = (20, 26, 38, 230)
COLOR_CARD_BORDER = (45, 60, 85)
COLOR_CYAN_ACCENT = (0, 210, 255)
COLOR_GREEN_ACCENT = (34, 215, 96)
COLOR_GOLD_ACCENT = (255, 200, 50)
COLOR_RED_ACCENT = (255, 70, 70)
COLOR_OVERLAY = (8, 12, 18, 210)
