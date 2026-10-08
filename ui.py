"""
SCPL Simulation - User Interface System
Provides buttons, interactive sliders for real-time physics parameters,
dark glassmorphic panels, telemetry HUD, and animated celebration text.
"""
import pygame
import math
import random
from config import *
import assets

class Button:
    def __init__(self, x, y, width, height, text, action=None, color_scheme="default", font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color_scheme = color_scheme
        self.font_size = font_size
        self.hovered = False
        self.pressed = False
        self.anim_scale = 0.0

    def draw(self, surface):
        # Smooth hover scale transition
        target_anim = 1.0 if self.hovered else 0.0
        self.anim_scale += (target_anim - self.anim_scale) * 0.25

        draw_rect = self.rect.copy()
        draw_rect.y -= int(self.anim_scale * 3)

        # Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, (10, 14, 20, 180), shadow_rect, border_radius=12)

        # Color schemes
        if self.color_scheme == "green":
            bg_color = (34, 180, 85) if not self.hovered else (45, 215, 105)
            border_color = (120, 255, 170) if self.hovered else (30, 140, 70)
            text_color = COLOR_WHITE
        elif self.color_scheme == "cyan":
            bg_color = (15, 120, 160) if not self.hovered else (20, 160, 210)
            border_color = COLOR_CYAN_ACCENT if self.hovered else (30, 90, 130)
            text_color = COLOR_WHITE
        elif self.color_scheme == "red":
            bg_color = (170, 40, 40) if not self.hovered else (210, 50, 50)
            border_color = (255, 120, 120) if self.hovered else (120, 30, 30)
            text_color = COLOR_WHITE
        elif self.color_scheme == "gold":
            bg_color = (190, 140, 20) if not self.hovered else (230, 175, 30)
            border_color = COLOR_GOLD_ACCENT if self.hovered else (140, 100, 15)
            text_color = (20, 20, 20)
        else: # default dark glass
            bg_color = (35, 45, 62) if not self.hovered else (50, 65, 90)
            border_color = (80, 110, 150) if self.hovered else (45, 60, 85)
            text_color = COLOR_WHITE

        if self.pressed:
            draw_rect.y += 2

        # Card Background & Border
        pygame.draw.rect(surface, bg_color, draw_rect, border_radius=12)
        pygame.draw.rect(surface, border_color, draw_rect, 2, border_radius=12)

        # Render Text with crisp shadow
        font = assets.get_font(self.font_size, bold=True)
        t_surf = font.render(self.text, True, text_color)
        t_rect = t_surf.get_rect(center=draw_rect.center)
        
        # Subtle text shadow
        t_shadow = font.render(self.text, True, (10, 15, 20))
        surface.blit(t_shadow, (t_rect.x + 1, t_rect.y + 1))
        surface.blit(t_surf, t_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.action:
                    self.action()
                return True
            self.pressed = False
        return False


class Slider:
    """
    Interactive horizontal slider control with unbounded dynamic scaling,
    built-in [-] and [+] stepper buttons, and mouse wheel scrolling.
    """
    def __init__(self, x, y, width, height, title, min_val, max_val, current_val, 
                 step=0.1, unit="", dynamic_max=False, on_change=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.min_val = min_val
        self.max_val = max(max_val, current_val)
        self.val = current_val
        self.step = step
        self.unit = unit
        self.dynamic_max = dynamic_max
        self.on_change = on_change
        
        self.dragging = False
        self.track_rect = pygame.Rect(x, y + 26, width, 8)
        self.handle_radius = 11

        # Interactive [-] and [+] stepper buttons
        btn_s = 20
        self.btn_minus_rect = pygame.Rect(self.rect.right - 100, self.rect.y - 1, btn_s, btn_s)
        self.btn_plus_rect = pygame.Rect(self.rect.right - btn_s, self.rect.y - 1, btn_s, btn_s)
        self.hover_minus = False
        self.hover_plus = False

    @property
    def handle_x(self):
        denom = max(0.001, self.max_val - self.min_val)
        ratio = (self.val - self.min_val) / denom
        ratio = max(0.0, min(1.0, ratio))
        return int(self.rect.x + ratio * self.rect.width)

    def set_value(self, new_val):
        if self.dynamic_max:
            if new_val > self.max_val:
                self.max_val = round(new_val * 1.15, 1)
            self.val = max(self.min_val, new_val)
        else:
            self.val = max(self.min_val, min(self.max_val, new_val))
        
        if self.step in (0.1, 0.2, 0.5):
            self.val = round(self.val, 1)
        elif isinstance(self.step, float) and self.step < 1:
            self.val = round(self.val, 2)
        
        if self.on_change:
            self.on_change(self.val)

    def draw(self, surface):
        # 1. Title Label on Left
        font_lbl = assets.get_font(17, bold=True)
        title_surf = font_lbl.render(self.title, True, COLOR_WHITE)
        surface.blit(title_surf, (self.rect.x, self.rect.y))

        # 2. Value Readout formatted cleanly
        if self.step in (0.1, 0.2, 0.5):
            val_str = f"{self.val:.1f}{self.unit}"
        elif isinstance(self.step, float) and self.step < 1:
            val_str = f"{self.val:.2f}{self.unit}"
        else:
            val_str = f"{int(self.val)}{self.unit}"
        
        font_val = assets.get_mono_font(15, bold=True)
        val_surf = font_val.render(val_str, True, COLOR_CYAN_ACCENT)
        
        # Position value text neatly between minus and plus buttons
        val_center_x = (self.btn_minus_rect.right + self.btn_plus_rect.left) // 2
        val_rect = val_surf.get_rect(center=(val_center_x, self.btn_plus_rect.centery))
        
        # Dynamically adjust minus button if value string is wide
        if val_rect.left < self.btn_minus_rect.right + 4:
            shift = (self.btn_minus_rect.right + 4) - val_rect.left
            self.btn_minus_rect.x = max(self.rect.x + 120, self.btn_minus_rect.x - shift)
            val_center_x = (self.btn_minus_rect.right + self.btn_plus_rect.left) // 2
            val_rect = val_surf.get_rect(center=(val_center_x, self.btn_plus_rect.centery))

        surface.blit(val_surf, val_rect)

        # 3. Stepper Buttons [-] and [+]
        # Minus button
        bg_m = (40, 55, 75) if not self.hover_minus else (60, 85, 115)
        border_m = COLOR_CYAN_ACCENT if self.hover_minus else (60, 80, 110)
        pygame.draw.rect(surface, bg_m, self.btn_minus_rect, border_radius=4)
        pygame.draw.rect(surface, border_m, self.btn_minus_rect, 1, border_radius=4)
        m_surf = font_lbl.render("-", True, COLOR_WHITE)
        surface.blit(m_surf, m_surf.get_rect(center=self.btn_minus_rect.center))

        # Plus button
        bg_p = (40, 55, 75) if not self.hover_plus else (60, 85, 115)
        border_p = COLOR_CYAN_ACCENT if self.hover_plus else (60, 80, 110)
        pygame.draw.rect(surface, bg_p, self.btn_plus_rect, border_radius=4)
        pygame.draw.rect(surface, border_p, self.btn_plus_rect, 1, border_radius=4)
        p_surf = font_lbl.render("+", True, COLOR_WHITE)
        surface.blit(p_surf, p_surf.get_rect(center=self.btn_plus_rect.center))

        # 4. Track Background
        pygame.draw.rect(surface, (25, 32, 45), self.track_rect, border_radius=4)
        pygame.draw.rect(surface, (45, 58, 80), self.track_rect, 1, border_radius=4)

        # 5. Active Fill Track
        hx = self.handle_x
        active_rect = pygame.Rect(self.rect.x, self.track_rect.y, max(0, hx - self.rect.x), self.track_rect.height)
        pygame.draw.rect(surface, COLOR_CYAN_ACCENT, active_rect, border_radius=4)

        # 6. Handle Knob
        hy = self.track_rect.centery
        handle_color = (240, 245, 255) if not self.dragging else COLOR_WHITE
        glow_surf = pygame.Surface((self.handle_radius * 4, self.handle_radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 210, 255, 60), (self.handle_radius * 2, self.handle_radius * 2), self.handle_radius + 4)
        surface.blit(glow_surf, (hx - self.handle_radius * 2, hy - self.handle_radius * 2))

        pygame.draw.circle(surface, handle_color, (hx, hy), self.handle_radius)
        pygame.draw.circle(surface, (20, 26, 38), (hx, hy), self.handle_radius, 2)
        pygame.draw.circle(surface, COLOR_CYAN_ACCENT, (hx, hy), 4)

    def handle_event(self, event):
        hy = self.track_rect.centery
        if event.type == pygame.MOUSEMOTION:
            self.hover_minus = self.btn_minus_rect.collidepoint(event.pos)
            self.hover_plus = self.btn_plus_rect.collidepoint(event.pos)
            if self.dragging:
                self._update_val_from_mouse(event.pos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Click minus button
            if self.btn_minus_rect.collidepoint((mx, my)):
                mult = 5 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                self.set_value(self.val - self.step * mult)
                return True
            # Click plus button
            elif self.btn_plus_rect.collidepoint((mx, my)):
                mult = 5 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                self.set_value(self.val + self.step * mult)
                return True
            # Click near track or knob
            elif self.rect.x - 10 <= mx <= self.rect.right + 10 and abs(my - hy) < 22:
                self.dragging = True
                self._update_val_from_mouse(mx)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True

        elif event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                mult = 5 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                self.set_value(self.val + event.y * self.step * mult)
                return True

        return False

    def _update_val_from_mouse(self, mouse_x):
        ratio = (mouse_x - self.rect.x) / max(1.0, float(self.rect.width))
        if self.dynamic_max:
            # Dynamically expand upper limit when dragged near or past right edge
            if ratio > 0.94:
                expand = 1.0 + (ratio - 0.94) * 1.5
                self.max_val = max(self.max_val * expand, self.max_val + self.step * 10)
                self.max_val = round(self.max_val, 1)
            ratio = min(1.0, max(0.0, (mouse_x - self.rect.x) / max(1.0, float(self.rect.width))))
        else:
            ratio = max(0.0, min(1.0, ratio))

        raw_val = self.min_val + ratio * (self.max_val - self.min_val)
        if self.step > 0:
            snapped = round(raw_val / self.step) * self.step
            if not self.dynamic_max:
                snapped = max(self.min_val, min(self.max_val, snapped))
            else:
                snapped = max(self.min_val, snapped)
            self.set_value(snapped)
        else:
            self.set_value(raw_val)


class TelemetryHUD:
    """
    Renders live scientific computing and kinematics telemetry on screen.
    """
    def __init__(self, x=20, y=80, width=320, height=210):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True

    def draw(self, surface, gravity_val, ball, stick_figure, initial_angle, initial_speed):
        if not self.visible:
            return

        # Semi-transparent dark glass panel
        panel = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (16, 22, 32, 220), (0, 0, self.rect.width, self.rect.height), border_radius=12)
        pygame.draw.rect(panel, (40, 56, 80, 255), (0, 0, self.rect.width, self.rect.height), 2, border_radius=12)
        surface.blit(panel, self.rect.topleft)

        # Header
        f_header = assets.get_font(18, bold=True)
        h_surf = f_header.render("PHYSICS TELEMETRY", True, COLOR_CYAN_ACCENT)
        surface.blit(h_surf, (self.rect.x + 16, self.rect.y + 12))

        # Metrics lines
        f_mono = assets.get_mono_font(15)
        
        # Telemetry fields
        curr_speed = ball.speed_mps if (ball and ball.launched) else 0.0
        curr_height = ball.height_meters if ball else 0.0
        curr_ke = ball.kinetic_energy if (ball and ball.launched) else 0.0
        dist_to_target = abs(stick_figure.x - (ball.x if ball else DEFAULT_BOW_X)) / PIXELS_PER_METER

        metrics = [
            ("Gravity (g):", f"{gravity_val:.2f} m/s^2"),
            ("Launch Angle (deg):", f"{initial_angle:.1f} deg"),
            ("Launch Speed (v0):", f"{initial_speed:.2f} m/s"),
            ("Current Speed |v|:", f"{curr_speed:.2f} m/s"),
            ("Height (y):", f"{curr_height:.2f} m"),
            ("Kinetic Energy:", f"{curr_ke:.2f} J"),
            ("Distance to Target:", f"{dist_to_target:.2f} m")
        ]

        for i, (label, val) in enumerate(metrics):
            ly = self.rect.y + 40 + i * 23
            lbl_surf = f_mono.render(label, True, COLOR_MUTED)
            val_surf = f_mono.render(val, True, COLOR_WHITE)
            surface.blit(lbl_surf, (self.rect.x + 16, ly))
            surface.blit(val_surf, (self.rect.right - 16 - val_surf.get_width(), ly))


class GameCompletedBanner:
    """
    Renders simple static text 'GAME COMPLETED' in green font with a thin white border.
    """
    def __init__(self):
        pass

    def reset(self):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        font = assets.get_font(62, bold=True)
        text_str = "GAME COMPLETED"
        cx, cy = WIDTH // 2, 210

        # 1. Thin white border (outline)
        outline_surf = font.render(text_str, True, COLOR_WHITE)
        out_rect = outline_surf.get_rect(center=(cx, cy))
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            surface.blit(outline_surf, (out_rect.x + dx, out_rect.y + dy))

        # 2. Main green font
        main_surf = font.render(text_str, True, COLOR_GREEN_ACCENT)
        surface.blit(main_surf, out_rect)
