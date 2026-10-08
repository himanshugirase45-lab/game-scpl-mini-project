"""
SCPL Simulation - Menu States & Educational Screens
Implements MainMenu, HowToPlay, AboutGame (Scientific Computing & Physics breakdown),
and InGameSettingsModal for live physics parameter manipulation.
"""
import pygame
import math
from config import *
import assets
import ui
from level import LEVEL_CONFIG
import save_manager

class GameState:
    """Base game state class."""
    def __init__(self, manager):
        self.manager = manager

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class MainMenu(GameState):
    """
    Main Menu Screen with Play, How to Play, About Game, and Quit buttons.
    """
    def __init__(self, manager):
        super().__init__(manager)
        self.time = 0.0
        
        # Interactive UI buttons
        btn_w, btn_h = 290, 50
        center_x = WIDTH // 2 - btn_w // 2
        start_y = 230
        spacing = 60

        self.buttons = [
            ui.Button(center_x, start_y, btn_w, btn_h, "PLAY SIMULATION", 
                      self.start_game, color_scheme="green", font_size=21),
            ui.Button(center_x, start_y + spacing, btn_w, btn_h, "LEVEL SELECT", 
                      self.open_level_select, color_scheme="cyan", font_size=20),
            ui.Button(center_x, start_y + spacing * 2, btn_w, btn_h, "HOW TO PLAY", 
                      self.open_how_to_play, color_scheme="cyan", font_size=19),
            ui.Button(center_x, start_y + spacing * 3, btn_w, btn_h, "ABOUT GAME & PHYSICS", 
                      self.open_about_game, color_scheme="default", font_size=18),
            ui.Button(center_x, start_y + spacing * 4, btn_w, btn_h, "EXIT", 
                      self.manager.quit, color_scheme="red", font_size=20)
        ]

    def open_level_select(self):
        self.manager.change_state(LevelSelect(self.manager))

    def start_game(self):
        from state_machine import PlayingState
        self.manager.change_state(PlayingState(self.manager))

    def open_how_to_play(self):
        self.manager.change_state(HowToPlay(self.manager))

    def open_about_game(self):
        self.manager.change_state(AboutGame(self.manager))

    def handle_events(self, events):
        for e in events:
            for b in self.buttons:
                b.handle_event(e)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        # 1. Dark background with fence and ground
        assets.draw_dark_background(surface)
        assets.draw_fence(surface)
        assets.draw_ground(surface)

        # 2. Decorative preview bow and red ball on left
        assets.draw_bow_structure(surface, DEFAULT_BOW_X, DEFAULT_BOW_HEIGHT)
        assets.draw_red_ball(surface, DEFAULT_BOW_X, DEFAULT_BOW_HEIGHT - 22, DEFAULT_BALL_RADIUS)

        # 3. Decorative preview white stick figure on right
        target_x = DEFAULT_BOW_X + DEFAULT_STICKMAN_DISTANCE
        assets.draw_white_stick_figure(surface, (target_x, GROUND_Y - 95), is_hit=False, ground_y=GROUND_Y)

        # 4. Title & Scientific Subtitle with glowing shadow
        title_font = assets.get_font(52, bold=True)
        title_text = "PROJECTILE MOTION SIMULATION"
        t_shadow = title_font.render(title_text, True, (0, 0, 0))
        t_surf = title_font.render(title_text, True, COLOR_WHITE)
        t_rect = t_surf.get_rect(center=(WIDTH // 2, 120))
        surface.blit(t_shadow, (t_rect.x + 3, t_rect.y + 3))
        surface.blit(t_surf, t_rect)

        # Subtitle badge
        sub_font = assets.get_font(20, bold=True)
        sub_text = "Scientific Computing with Python"
        s_surf = sub_font.render(sub_text, True, COLOR_CYAN_ACCENT)
        s_rect = s_surf.get_rect(center=(WIDTH // 2, t_rect.bottom + 22))
        surface.blit(s_surf, s_rect)

        # 5. Render Buttons
        for b in self.buttons:
            b.draw(surface)


class HowToPlay(GameState):
    """
    Instructions screen explaining controls, physics tuning, and winning objectives.
    """
    def __init__(self, manager):
        super().__init__(manager)
        self.buttons = [
            ui.Button(WIDTH // 2 - 240, 630, 220, 50, "BACK TO MENU", 
                      lambda: self.manager.change_state(MainMenu(self.manager)), color_scheme="default"),
            ui.Button(WIDTH // 2 + 20, 630, 220, 50, "PLAY NOW", 
                      self.start_game, color_scheme="green")
        ]

    def open_level_select(self):
        self.manager.change_state(LevelSelect(self.manager))

    def start_game(self):
        from state_machine import PlayingState
        self.manager.change_state(PlayingState(self.manager))

    def handle_events(self, events):
        for e in events:
            for b in self.buttons:
                b.handle_event(e)

    def draw(self, surface):
        assets.draw_dark_background(surface)
        assets.draw_fence(surface)
        assets.draw_ground(surface)

        # Dark glass container card
        card_rect = pygame.Rect(WIDTH // 2 - 480, 50, 960, 550)
        panel = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, COLOR_CARD_BG, (0, 0, card_rect.width, card_rect.height), border_radius=16)
        pygame.draw.rect(panel, COLOR_CARD_BORDER, (0, 0, card_rect.width, card_rect.height), 2, border_radius=16)
        surface.blit(panel, card_rect.topleft)

        # Title
        f_title = assets.get_font(38, bold=True)
        t_surf = f_title.render("HOW TO PLAY & CONTROLS", True, COLOR_CYAN_ACCENT)
        surface.blit(t_surf, (card_rect.x + 35, card_rect.y + 25))

        # Instructions Steps
        instructions = [
            ("1. Aiming & Slingshot Pull", 
             "Click and drag the RED BALL backwards from the bow structure. The farther you pull, the greater the launch force."),
            ("2. Real-time Trajectory Kinematics", 
             "Observe the dotted parabolic trajectory arc generated live using ballistic kinematic equations."),
            ("3. Release to Launch", 
             "Release the mouse button to fire the ball under realistic gravitational acceleration (default g = 9.8 m/s^2)."),
            ("4. Target Objective", 
             "Hit the WHITE STICK FIGURE standing downfield to trigger the victory celebration and complete the simulation!"),
            ("5. Realistic Bounces & Restitution", 
             "When the ball hits the ground, walls, or stick figure, it realistically bounces based on physical elasticity until settling."),
            ("6. Top Settings (Physics Customizer)", 
             "Click the top SETTINGS button at any time to modify Gravity, Ball/Ground/Target Elasticity, Bow Height, and Target Distance in real-time.")
        ]

        f_step_title = assets.get_font(20, bold=True)
        f_step_desc = assets.get_font(16)

        for i, (st, desc) in enumerate(instructions):
            sy = card_rect.y + 85 + i * 72
            # Step header
            h_surf = f_step_title.render(st, True, COLOR_GOLD_ACCENT)
            surface.blit(h_surf, (card_rect.x + 35, sy))
            # Step text
            d_surf = f_step_desc.render(desc, True, COLOR_WHITE)
            surface.blit(d_surf, (card_rect.x + 35, sy + 26))

        for b in self.buttons:
            b.draw(surface)


class AboutGame(GameState):
    """
    Educational screen showcasing how the game applies Physics and Scientific Computing in Python.
    """
    def __init__(self, manager):
        super().__init__(manager)
        self.buttons = [
            ui.Button(WIDTH // 2 - 240, 630, 220, 50, "BACK TO MENU", 
                      lambda: self.manager.change_state(MainMenu(self.manager)), color_scheme="default"),
            ui.Button(WIDTH // 2 + 20, 630, 220, 50, "START SIMULATION", 
                      self.start_game, color_scheme="green")
        ]

    def open_level_select(self):
        self.manager.change_state(LevelSelect(self.manager))

    def start_game(self):
        from state_machine import PlayingState
        self.manager.change_state(PlayingState(self.manager))

    def handle_events(self, events):
        for e in events:
            for b in self.buttons:
                b.handle_event(e)

    def draw(self, surface):
        assets.draw_dark_background(surface)
        assets.draw_fence(surface)
        assets.draw_ground(surface)

        card_rect = pygame.Rect(WIDTH // 2 - 520, 45, 1040, 565)
        panel = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, COLOR_CARD_BG, (0, 0, card_rect.width, card_rect.height), border_radius=16)
        pygame.draw.rect(panel, COLOR_CARD_BORDER, (0, 0, card_rect.width, card_rect.height), 2, border_radius=16)
        surface.blit(panel, card_rect.topleft)

        # Title
        f_title = assets.get_font(34, bold=True)
        t_surf = f_title.render("PHYSICS & SCIENTIFIC COMPUTING IN PYTHON", True, COLOR_CYAN_ACCENT)
        surface.blit(t_surf, (card_rect.x + 30, card_rect.y + 20))

        # Scientific sections
        sections = [
            ("1. Classical Projectile Kinematics (g = 9.8 m/s^2)",
             "Decomposes 2D motion: x(t) = x0 + v0*cos(theta)*t and y(t) = y0 + v0*sin(theta)*t + 0.5*g*t^2.\nPredicts range R = (v0^2 * sin(2*theta))/g and apex height H = (v0^2 * sin^2(theta))/(2*g) in real-time."),
            
            ("2. Hooke's Law & Elastic Potential Energy",
             "When pulling the slingshot, tension behaves like an elastic spring: F = -k*dx.\nStored potential energy U = 0.5*k*(dx)^2 converts to kinetic energy Ek = 0.5*m*v0^2 at launch."),
            
            ("3. Collision Dynamics & Coefficient of Restitution (e)",
             "Rebound velocities are modeled via restitution e = v_separation / v_approach.\nImpulses J = -(1+e)*(v_rel . n)/(1/m1 + 1/m2) determine realistic bounces off ground & target."),
            
            ("4. Symplectic Numerical Integration in Python",
             "Utilizes Pymunk (Chipmunk2D engine) to perform high-frequency sub-stepping (600 Hz)\nsolving Newton's differential equations of motion with rigorous momentum conservation.")
        ]

        f_sec_title = assets.get_font(19, bold=True)
        f_sec_desc = assets.get_font(15)

        for i, (title, text) in enumerate(sections):
            sy = card_rect.y + 75 + i * 110
            # Header
            h_surf = f_sec_title.render(title, True, COLOR_GOLD_ACCENT)
            surface.blit(h_surf, (card_rect.x + 30, sy))

            # Multi-line text
            lines = text.split('\n')
            for j, line in enumerate(lines):
                l_surf = f_sec_desc.render(line, True, COLOR_WHITE)
                surface.blit(l_surf, (card_rect.x + 30, sy + 26 + j * 24))

        for b in self.buttons:
            b.draw(surface)


class InGameSettingsModal:
    """
    Floating settings panel opened via the top Menu button.
    Allows real-time tweaking of:
    - Gravity (g)
    - Ball Elasticity
    - Ground Elasticity
    - Stick Figure Elasticity
    - Stick Figure Distance
    - Bow Height
    """
    def __init__(self, playing_state):
        self.state = playing_state
        self.w, self.h = 680, 580
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT // 2 - self.h // 2

        # Sliders for physical parameters
        slider_w = 280
        col1_x = self.x + 40
        col2_x = self.x + 360
        start_y = self.y + 90
        spacing = 80

        self.sliders = [
            ui.Slider(col1_x, start_y, slider_w, 55, "Gravity (g)", 
                      0.0, 25.0, self.state.gravity_val, step=0.1, unit=" m/s^2", 
                      dynamic_max=True, on_change=self.state.set_gravity),
            
            ui.Slider(col1_x, start_y + spacing, slider_w, 55, "Ball Elasticity", 
                      0.0, 1.0, self.state.ball_elasticity, step=0.05, unit="", 
                      dynamic_max=False, on_change=self.state.set_ball_elasticity),
            
            ui.Slider(col1_x, start_y + spacing * 2, slider_w, 55, "Ground Elasticity", 
                      0.0, 1.0, self.state.ground_elasticity, step=0.05, unit="", 
                      dynamic_max=False, on_change=self.state.set_ground_elasticity),

            ui.Slider(col2_x, start_y, slider_w, 55, "Stick Figure Elasticity", 
                      0.0, 1.0, self.state.stickman_elasticity, step=0.05, unit="", 
                      dynamic_max=False, on_change=self.state.set_stickman_elasticity),

            ui.Slider(col2_x, start_y + spacing, slider_w, 55, "Target Distance", 
                      MIN_STICKMAN_DISTANCE_M, INITIAL_MAX_STICKMAN_DISTANCE_M, self.state.stickman_distance_m, step=0.5, unit=" m", 
                      dynamic_max=True, on_change=self.state.set_stickman_distance_m),

            ui.Slider(col2_x, start_y + spacing * 2, slider_w, 55, "Bow Height (Elevation)", 
                      MIN_BOW_ELEVATION_M, INITIAL_MAX_BOW_ELEVATION_M, self.state.bow_elevation_m, step=0.2, unit=" m", 
                      dynamic_max=True, on_change=self.state.set_bow_elevation_m)
        ]

        # Preset Gravity Buttons
        self.preset_buttons = [
            ui.Button(self.x + 40, self.y + 355, 115, 36, "Earth (9.8)", lambda: self._apply_preset(9.8), font_size=15),
            ui.Button(self.x + 165, self.y + 355, 115, 36, "Moon (1.6)", lambda: self._apply_preset(1.6), font_size=15),
            ui.Button(self.x + 290, self.y + 355, 115, 36, "Mars (3.7)", lambda: self._apply_preset(3.7), font_size=15),
            ui.Button(self.x + 415, self.y + 355, 115, 36, "Jupiter (24.8)", lambda: self._apply_preset(24.8), font_size=15),
            ui.Button(self.x + 540, self.y + 355, 100, 36, "Zero-G", lambda: self._apply_preset(0.0), font_size=15)
        ]

        # Action Buttons
        btn_y = self.y + 495
        self.action_buttons = [
            ui.Button(self.x + 40, btn_y, 180, 50, "RESET BALL", 
              self.state.reload_ball, color_scheme="cyan", font_size=18),
            ui.Button(self.x + 240, btn_y, 190, 50, "MAIN MENU", 
                      lambda: self.state.manager.change_state(MainMenu(self.state.manager)), color_scheme="default", font_size=18),
            ui.Button(self.x + 450, btn_y, 190, 50, "RESUME", 
                      self.state.close_menu, color_scheme="green", font_size=18)
        ]

    def _apply_preset(self, g_val):
        self.sliders[0].set_value(g_val)

    def handle_event(self, event):
        for s in self.sliders:
            if s.handle_event(event):
                return True
        for b in self.preset_buttons:
            if b.handle_event(event):
                return True
        for b in self.action_buttons:
            if b.handle_event(event):
                return True
        return False

    def draw(self, surface):
        # Soft transparent overlay behind modal so background zoom is visible
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 18, 150))
        surface.blit(overlay, (0, 0))

        # Modal Card
        panel = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(panel, COLOR_CARD_BG, (0, 0, self.w, self.h), border_radius=18)
        pygame.draw.rect(panel, (60, 85, 120), (0, 0, self.w, self.h), 2, border_radius=18)
        surface.blit(panel, (self.x, self.y))

        # Header Title
        f_title = assets.get_font(28, bold=True)
        t_surf = f_title.render("PHYSICS & ENVIRONMENT CONTROLS", True, COLOR_CYAN_ACCENT)
        surface.blit(t_surf, (self.x + 40, self.y + 26))

        # Preset label
        f_lbl = assets.get_font(16, bold=True)
        p_lbl = f_lbl.render("Quick Gravity Presets:", True, COLOR_MUTED)
        surface.blit(p_lbl, (self.x + 40, self.y + 330))

        # Draw Sliders & Buttons
        for s in self.sliders:
            s.draw(surface)
        for b in self.preset_buttons:
            b.draw(surface)
        for b in self.action_buttons:
            b.draw(surface)

class LevelSelect(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.save_data = save_manager.load_save()
        
        self.btn_back = ui.Button(20, 20, 150, 50, "BACK", 
                      lambda: self.manager.change_state(MainMenu(self.manager)), color_scheme="default")
        
        self.level_buttons = []
        start_x = 100
        start_y = 150
        spacing_x = 220
        spacing_y = 200
        
        for i, (lvl_id, lvl_data) in enumerate(LEVEL_CONFIG.items()):
            x = start_x + (i % 5) * spacing_x
            y = start_y + (i // 5) * spacing_y
            
            unlocked = self.save_data['levels'].get(str(lvl_id), {}).get('unlocked', False)
            if lvl_id == 1: unlocked = True # Level 1 always unlocked
            
            stars = self.save_data['levels'].get(str(lvl_id), {}).get('stars', 0)
            score = self.save_data['levels'].get(str(lvl_id), {}).get('score', 0)
            
            def make_action(l_id=lvl_id):
                return lambda: self.start_level(l_id)
            
            action = make_action() if unlocked else None
            scheme = "green" if unlocked else "red"
            text = f"Level {lvl_id}\n{lvl_data['name']}\n" + ("Locked" if not unlocked else f"Stars: {stars}")
            
            btn = ui.Button(x, y, 200, 150, text, action=action, color_scheme=scheme, font_size=16)
            self.level_buttons.append(btn)

    def start_level(self, level_id):
        from state_machine import PlayingState
        self.manager.change_state(PlayingState(self.manager, level_id=level_id))

    def handle_events(self, events):
        for e in events:
            self.btn_back.handle_event(e)
            for b in self.level_buttons:
                b.handle_event(e)

    def draw(self, surface):
        assets.draw_dark_background(surface)
        assets.draw_fence(surface)
        assets.draw_ground(surface)
        
        f_title = assets.get_font(48, bold=True)
        t_surf = f_title.render("SELECT LEVEL", True, COLOR_CYAN_ACCENT)
        surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 40))
        
        self.btn_back.draw(surface)
        for b in self.level_buttons:
            b.draw(surface)
