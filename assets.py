"""
SCPL Simulation - Assets & Visual Generators
Provides procedural graphics, dark-themed scenery, fence, bow structure, 
red ball, white stick figure, fonts, and particle visual effects with full camera zoom support.
"""
import pygame
import math
import random
from config import *

pygame.init()

_font_cache = {}
_surf_cache = {}

def get_font(size, bold=False, italic=False):
    """Retrieve or cache a modern system font with clean fallbacks."""
    key = f"font_{size}_{bold}_{italic}"
    if key not in _font_cache:
        font_names = ["segoeui", "inter", "roboto", "arial", "helvetica", "trebuchetms"]
        selected_font = None
        for name in font_names:
            try:
                selected_font = pygame.font.SysFont(name, size, bold=bold, italic=italic)
                if selected_font:
                    break
            except Exception:
                continue
        if not selected_font:
            selected_font = pygame.font.Font(None, size)
        _font_cache[key] = selected_font
    return _font_cache[key]

def get_mono_font(size, bold=False):
    """Retrieve monospace font for scientific telemetry data."""
    key = f"mono_{size}_{bold}"
    if key not in _font_cache:
        for name in ["consolas", "cascadiacode", "couriernew", "monospace"]:
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f:
                    _font_cache[key] = f
                    return f
            except Exception:
                pass
        _font_cache[key] = pygame.font.Font(None, size)
    return _font_cache[key]

def draw_dark_background(surface, width=WIDTH, height=HEIGHT):
    """Draws a sleek, dark-themed gradient background with atmospheric night glow."""
    key = f"dark_bg_{width}_{height}"
    if key not in _surf_cache:
        bg = pygame.Surface((width, height))
        
        # Smooth vertical dark gradient
        for y in range(height):
            ratio = y / height
            r = int(COLOR_BG_DARK_TOP[0] * (1 - ratio) + COLOR_BG_DARK_BOTTOM[0] * ratio)
            g = int(COLOR_BG_DARK_TOP[1] * (1 - ratio) + COLOR_BG_DARK_BOTTOM[1] * ratio)
            b = int(COLOR_BG_DARK_TOP[2] * (1 - ratio) + COLOR_BG_DARK_BOTTOM[2] * ratio)
            pygame.draw.line(bg, (r, g, b), (0, y), (width, y))
            
        # Subtle distant star field
        random.seed(42)
        for _ in range(70):
            sx = random.randint(0, width)
            sy = random.randint(0, int(height * 0.7))
            brightness = random.randint(60, 160)
            star_size = random.choice([1, 1, 2])
            pygame.draw.circle(bg, (brightness, brightness, brightness + 30), (sx, sy), star_size)
            
        _surf_cache[key] = bg

    surface.blit(_surf_cache[key], (0, 0))

def draw_fence(surface, width=WIDTH, ground_y=GROUND_Y, camera=None):
    """Draws a wooden/dark aesthetic fence across the background."""
    zoom = camera.zoom if camera else 1.0
    
    def to_screen(wx, wy):
        return camera.world_to_screen(wx, wy) if camera else (wx, wy)

    fence_top_world = ground_y - 110
    fence_bottom_world = ground_y

    # Calculate visible world horizontal span
    if camera:
        w_left, _ = camera.screen_to_world(-50, 0)
        w_right, _ = camera.screen_to_world(width + 50, 0)
    else:
        w_left, w_right = -50, width + 50

    # Horizontal rails
    rail_y1_s = to_screen(0, fence_top_world + 30)[1]
    rail_y2_s = to_screen(0, fence_top_world + 85)[1]
    rail_h = max(2, int(12 * zoom))
    
    pygame.draw.rect(surface, COLOR_FENCE_SHADOW, (0, rail_y1_s - 1, width, rail_h + 2))
    pygame.draw.rect(surface, COLOR_FENCE_WOOD, (0, rail_y1_s, width, rail_h))
    pygame.draw.rect(surface, COLOR_FENCE_SHADOW, (0, rail_y2_s - 1, width, rail_h + 2))
    pygame.draw.rect(surface, COLOR_FENCE_WOOD, (0, rail_y2_s, width, rail_h))

    if zoom < 0.15:
        # Optimized simple fence for ultra-wide zoom
        return

    # Vertical pickets
    picket_step = 46
    start_i = int(w_left / picket_step) - 1
    end_i = int(w_right / picket_step) + 2

    for i in range(start_i, end_i):
        wx = i * picket_step
        sx, sy_top = to_screen(wx, fence_top_world)
        _, sy_bot = to_screen(wx, fence_bottom_world)

        if -50 <= sx <= width + 50:
            pw = max(3, int(22 * zoom))
            p_rect = pygame.Rect(int(sx), int(sy_top), pw, int(sy_bot - sy_top))
            pygame.draw.rect(surface, COLOR_FENCE_SHADOW, (p_rect.x + 2, p_rect.y + 2, p_rect.w, p_rect.h))
            pygame.draw.rect(surface, COLOR_FENCE_WOOD, p_rect)
            pygame.draw.rect(surface, COLOR_FENCE_SHADOW, p_rect, 1)

def draw_ground(surface, width=WIDTH, height=HEIGHT, ground_y=GROUND_Y, origin_x=DEFAULT_BOW_X, camera=None):
    """Draws the solid ground plane with metric scale zeroed at the bow origin."""
    zoom = camera.zoom if camera else 1.0
    
    def to_screen(wx, wy):
        return camera.world_to_screen(wx, wy) if camera else (wx, wy)

    _, ground_screen_y = to_screen(0, ground_y)
    ground_screen_y = int(ground_screen_y)

    # Dark earth rectangle from surface line to bottom
    ground_rect = pygame.Rect(0, ground_screen_y, width, max(0, height - ground_screen_y))
    pygame.draw.rect(surface, COLOR_GROUND_BASE, ground_rect)

    # Sub-layer accents
    accent_h = max(3, int(10 * zoom))
    pygame.draw.rect(surface, COLOR_GROUND_ACCENT, (0, ground_screen_y, width, accent_h))

    # Glowing cyan surface line
    pygame.draw.line(surface, COLOR_GROUND_LINE, (0, ground_screen_y), (width, ground_screen_y), max(2, int(3 * zoom)))

    # Comprehensive multi-tier adaptive metric scale tick step based on zoom
    if zoom >= 0.80:
        major_step = 2   # Label every 2m
        minor_step = 1   # Tick every 1m
    elif zoom >= 0.45:
        major_step = 5   # Label every 5m
        minor_step = 1   # Tick every 1m
    elif zoom >= 0.20:
        major_step = 10  # Label every 10m
        minor_step = 2   # Tick every 2m
    elif zoom >= 0.08:
        major_step = 25  # Label every 25m
        minor_step = 5   # Tick every 5m
    elif zoom >= 0.03:
        major_step = 50  # Label every 50m
        minor_step = 10  # Tick every 10m
    else:
        major_step = 100 # Label every 100m
        minor_step = 25  # Tick every 25m

    tick_font = get_font(max(10, min(14, int(12 * math.sqrt(max(0.2, zoom))))), bold=True)
    step_px = int(PIXELS_PER_METER) # 1 meter = 50 world px

    if camera:
        w_left, _ = camera.screen_to_world(-50, 0)
        w_right, _ = camera.screen_to_world(width + 50, 0)
    else:
        w_left, w_right = -50, width + 50

    m_start = int((w_left - origin_x) / (step_px * minor_step)) * minor_step - minor_step * 2
    m_end = int((w_right - origin_x) / (step_px * minor_step)) * minor_step + minor_step * 2

    for m in range(m_start, m_end, minor_step):
        world_px = origin_x + m * step_px
        sx, _ = to_screen(world_px, ground_y)
        sx = int(sx)
        if -30 <= sx <= width + 30:
            is_major = (m % major_step == 0)
            tick_len = int((10 if is_major else 5) * max(0.5, zoom))
            tick_w = max(1, int((2 if is_major else 1) * max(0.5, zoom)))
            pygame.draw.line(surface, (80, 110, 150), (sx, ground_screen_y), (sx, ground_screen_y + max(3, tick_len)), tick_w)
            
            if is_major:
                lbl_str = f"{m}m"
                lbl_color = COLOR_CYAN_ACCENT if m == 0 else (110, 140, 180)
                lbl = tick_font.render(lbl_str, True, lbl_color)
                surface.blit(lbl, (sx - lbl.get_width() // 2, ground_screen_y + max(4, tick_len) + 2))

def draw_bow_structure(surface, x, bow_y, ground_y=GROUND_Y, camera=None):
    """Draws the bow support stand and prongs transformed by the camera."""
    zoom = camera.zoom if camera else 1.0
    
    def to_screen(wx, wy):
        return camera.world_to_screen(wx, wy) if camera else (wx, wy)

    sx, s_bow_y = to_screen(x, bow_y)
    _, s_ground_y = to_screen(x, ground_y)
    
    post_w = max(4, int(18 * zoom))
    post_h = max(2, int(s_ground_y - s_bow_y))
    post_rect = pygame.Rect(int(sx - post_w // 2), int(s_bow_y), post_w, post_h)
    
    # Post shadow & body
    pygame.draw.rect(surface, (15, 18, 25), (post_rect.x + 2, post_rect.y + 2, post_rect.w, post_rect.h), border_radius=3)
    pygame.draw.rect(surface, COLOR_BOW_WOOD, post_rect, border_radius=3)
    pygame.draw.rect(surface, COLOR_BOW_DARK, post_rect, max(1, int(2 * zoom)), border_radius=3)

    # Scaffolding crossbars if elevated high
    if post_h > 80:
        rung_spacing = max(16, int(40 * zoom))
        for ry in range(int(s_bow_y) + rung_spacing, int(s_ground_y) - 10, rung_spacing):
            rw = max(6, int(28 * zoom))
            pygame.draw.rect(surface, COLOR_BOW_DARK, (int(sx - rw // 2), ry, rw, max(2, int(4 * zoom))), border_radius=1)

    # Base feet on ground
    base_w = max(10, int(46 * zoom))
    pygame.draw.rect(surface, COLOR_BOW_DARK, (int(sx - base_w // 2), int(s_ground_y - 4 * zoom), base_w, max(3, int(8 * zoom))), border_radius=2)

    # Fork prongs
    fork_h = 45
    prong_spread = 32

    s_lt = to_screen(x - prong_spread, bow_y - fork_h)
    s_rt = to_screen(x + prong_spread, bow_y - fork_h)
    s_stem = to_screen(x, bow_y + 4)

    line_w1 = max(3, int(10 * zoom))
    line_w2 = max(2, int(7 * zoom))
    cap_r = max(2, int(5 * zoom))

    # Left prong
    pygame.draw.line(surface, COLOR_BOW_DARK, s_stem, s_lt, line_w1)
    pygame.draw.line(surface, COLOR_BOW_WOOD, s_stem, s_lt, line_w2)
    pygame.draw.circle(surface, COLOR_BOW_DARK, (int(s_lt[0]), int(s_lt[1])), cap_r)

    # Right prong
    pygame.draw.line(surface, COLOR_BOW_DARK, s_stem, s_rt, line_w1)
    pygame.draw.line(surface, COLOR_BOW_WOOD, s_stem, s_rt, line_w2)
    pygame.draw.circle(surface, COLOR_BOW_DARK, (int(s_rt[0]), int(s_rt[1])), cap_r)

def draw_red_ball(surface, x, y, radius=DEFAULT_BALL_RADIUS, camera=None):
    """Draws a red sphere with 3D gradient shading and zoom scaling."""
    zoom = camera.zoom if camera else 1.0
    
    if camera:
        sx, sy = camera.world_to_screen(x, y)
    else:
        sx, sy = x, y

    int_x, int_y = int(sx), int(sy)
    r = max(5, int(radius * zoom))

    # Outer glow
    glow_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (235, 45, 45, 50), (r * 2, r * 2), r + max(3, int(5 * zoom)))
    surface.blit(glow_surf, (int_x - r * 2, int_y - r * 2))

    # Base sphere shadow & red body
    pygame.draw.circle(surface, COLOR_BALL_SHADOW, (int_x, int_y), r)
    pygame.draw.circle(surface, COLOR_BALL_RED, (int_x - 1, int_y - 1), max(1, r - 1))
    
    # 3D highlight glint
    shine_r = max(1, r // 3)
    pygame.draw.circle(surface, COLOR_BALL_SHINE, (int_x - r // 3, int_y - r // 3), shine_r)
    if r > 6:
        pygame.draw.circle(surface, COLOR_WHITE, (int_x - r // 3, int_y - r // 3), max(1, r // 6))

def draw_white_stick_figure(surface, body_or_pos, is_hit=False, ground_y=GROUND_Y, angle=0.0, camera=None):
    """
    Renders an articulated white stick figure at the target position,
    strictly clamped so all limbs remain on or above the ground surface line.
    """
    color = COLOR_STICKMAN_HIT if is_hit else COLOR_STICKMAN
    zoom = camera.zoom if camera else 1.0
    
    def to_screen(wx, wy):
        return camera.world_to_screen(wx, wy) if camera else (wx, wy)

    head_r = max(4, int(14 * zoom))

    if hasattr(body_or_pos, 'local_to_world'):
        body = body_or_pos
        head_raw = body.local_to_world((0, -38))
        neck_raw = body.local_to_world((0, -20))
        shoulder_raw = body.local_to_world((0, -16))
        hip_raw = body.local_to_world((0, 15))
        
        if not is_hit:
            lhand_raw = body.local_to_world((-18, 14))
            rhand_raw = body.local_to_world((18, 14))
            lfoot_raw = body.local_to_world((-14, 52))
            rfoot_raw = body.local_to_world((14, 52))
        else:
            lhand_raw = body.local_to_world((-22, -6))
            rhand_raw = body.local_to_world((24, 18))
            lfoot_raw = body.local_to_world((-20, 48))
            rfoot_raw = body.local_to_world((16, 52))
    else:
        sx, sy = body_or_pos
        head_raw = (sx, sy)
        neck_raw = (sx, sy + 18)
        shoulder_raw = (sx, sy + 22)
        hip_raw = (sx, sy + 60)
        lhand_raw = (sx - 18, shoulder_raw[1] + 24)
        rhand_raw = (sx + 18, shoulder_raw[1] + 24)
        lfoot_raw = (sx - 14, hip_raw[1] + 32)
        rfoot_raw = (sx + 14, hip_raw[1] + 32)

    # Convert to screen and clamp above ground
    _, ground_screen_y = to_screen(0, ground_y)

    def clamp_screen_pt(wpt, radius=0):
        sx, sy = to_screen(wpt[0], wpt[1])
        max_sy = ground_screen_y - radius - 1
        return (int(sx), int(min(max_sy, sy)))

    c_head = clamp_screen_pt(head_raw, radius=head_r)
    c_neck = clamp_screen_pt(neck_raw, radius=2)
    c_shoulder = clamp_screen_pt(shoulder_raw, radius=2)
    c_hip = clamp_screen_pt(hip_raw, radius=2)
    c_lhand = clamp_screen_pt(lhand_raw, radius=2)
    c_rhand = clamp_screen_pt(rhand_raw, radius=2)
    c_lfoot = clamp_screen_pt(lfoot_raw, radius=2)
    c_rfoot = clamp_screen_pt(rfoot_raw, radius=2)

    line_w_torso = max(2, int(4 * zoom))
    line_w_limb = max(2, int(3 * zoom))

    # 1. Head
    pygame.draw.circle(surface, color, c_head, head_r, max(2, int(3 * zoom)))
    pygame.draw.circle(surface, (20, 24, 34), c_head, max(1, head_r - 2))

    # 2. Torso / Spine
    pygame.draw.line(surface, color, c_neck, c_hip, line_w_torso)

    # 3. Arms
    pygame.draw.line(surface, color, c_shoulder, c_lhand, line_w_limb)
    pygame.draw.line(surface, color, c_shoulder, c_rhand, line_w_limb)

    # 4. Legs
    pygame.draw.line(surface, color, c_hip, c_lfoot, line_w_torso)
    pygame.draw.line(surface, color, c_hip, c_rfoot, line_w_torso)

    # 5. Distant Beacon / Target Indicator Arrow if zoomed far out
    if zoom < 0.45 and not is_hit:
        ind_y = c_head[1] - head_r - 10
        ind_pts = [
            (c_head[0], ind_y + 6),
            (c_head[0] - 6, ind_y),
            (c_head[0] + 6, ind_y)
        ]
        pygame.draw.polygon(surface, COLOR_CYAN_ACCENT, ind_pts)
