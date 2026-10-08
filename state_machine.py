"""
SCPL Simulation - Main Game Simulation State Machine
Orchestrates real-time 2D physics execution, dynamic camera zooming & framing,
slingshot drag-and-launch, collision detection, target response, live telemetry, and victory state.
"""
import pygame
import pymunk
import math
import random
from config import *
import assets
import ui
import physics
import save_manager
from level import LEVEL_CONFIG
from entities import Ball, StickFigure, Bow
import menus
from menus import GameState, MainMenu, InGameSettingsModal, LevelSelect

class Camera:
    """
    Dynamic camera that smoothly zooms in / zooms out and frames the scene
    so that the bow, stick figure, trajectory, and ground are always perfectly visible.
    """
    def __init__(self):
        self.zoom = 1.0
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.target_zoom = 1.0
        self.target_cam_x = 0.0
        self.target_cam_y = 0.0

    def update_targets(self, bow_x, bow_y, target_x, ground_y=GROUND_Y):
        # Bounding box in world coordinates
        x_min = bow_x - 110.0
        x_max = target_x + 90.0
        w_world = max(420.0, x_max - x_min)

        y_min = min(ground_y - 180.0, bow_y - 80.0)
        y_max = ground_y + 25.0
        h_world = max(320.0, y_max - y_min)

        pad_left = 65.0
        pad_right = 65.0
        pad_top = 80.0
        pad_bottom = 60.0

        zoom_w = (WIDTH - (pad_left + pad_right)) / w_world
        zoom_h = (HEIGHT - (pad_top + pad_bottom)) / h_world
        
        # Unbounded dynamic zoom (from ultra-wide macro view up to close-up)
        self.target_zoom = max(0.005, min(1.40, min(zoom_w, zoom_h)))

        self.target_cam_x = pad_left - x_min * self.target_zoom
        self.target_cam_y = (HEIGHT - pad_bottom) - ground_y * self.target_zoom

    def update(self, dt):
        # Smooth interpolation / camera spring
        lerp_speed = min(1.0, dt * 10.0)
        self.zoom += (self.target_zoom - self.zoom) * lerp_speed
        self.cam_x += (self.target_cam_x - self.cam_x) * lerp_speed
        self.cam_y += (self.target_cam_y - self.cam_y) * lerp_speed

    def world_to_screen(self, wx, wy):
        return (wx * self.zoom + self.cam_x, wy * self.zoom + self.cam_y)

    def screen_to_world(self, sx, sy):
        return ((sx - self.cam_x) / self.zoom, (sy - self.cam_y) / self.zoom)


class PlayingState(GameState):
    """
    Main interactive physics simulation sandbox state with dynamic zooming camera.
    """
    def __init__(self, manager, level_id=None):
        super().__init__(manager)
        self.level_id = level_id
        self.level_data = LEVEL_CONFIG.get(level_id) if level_id else None
        
        self.attempts_left = self.level_data["attempts"] if self.level_data else 999
        self.max_attempts = self.attempts_left
        self.level_failed = False
        self.obstacles = []
        self.moving_target = self.level_data["moving_target"] if self.level_data else False
        self.move_dir = 1.0
        self.target_base_x = 0
        self.level_title_timer = 3.0

        
        # Audio Initialization
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.sound_throw = pygame.mixer.Sound("throw.wav")
            self.sound_hit = pygame.mixer.Sound("hit.wav")
        except Exception:
            self.sound_throw = None
            self.sound_hit = None
        
        # Current Physics Parameters
        self.gravity_val = DEFAULT_GRAVITY
        self.ball_elasticity = DEFAULT_BALL_ELASTICITY
        self.ground_elasticity = DEFAULT_GROUND_ELASTICITY
        self.stickman_elasticity = DEFAULT_STICKMAN_ELASTICITY
        self.stickman_distance_m = self.level_data["target_distance_m"] if self.level_data else DEFAULT_STICKMAN_DISTANCE_M
        self.stickman_distance = self.stickman_distance_m * PIXELS_PER_METER
        self.target_ground = GROUND_Y - (self.level_data["target_elevation_m"] * PIXELS_PER_METER if self.level_data else 0)
        self.bow_elevation_m = DEFAULT_BOW_ELEVATION_M
        self.bow_elevation = DEFAULT_BOW_ELEVATION
        self.bow_height = GROUND_Y - self.bow_elevation
        
        # Dynamic Camera
        self.camera = Camera()
        self.camera.update_targets(DEFAULT_BOW_X, self.bow_height, DEFAULT_BOW_X + self.stickman_distance)
        self.camera.zoom = self.camera.target_zoom
        self.camera.cam_x = self.camera.target_cam_x
        self.camera.cam_y = self.camera.target_cam_y
        
        # Physics Space Initialization
        self.space = physics.create_physics_space(self.gravity_val)
        self.ground_shape = physics.create_ground(self.space, WIDTH * 4, HEIGHT, GROUND_Y, self.ground_elasticity)
        
        # Bow Structure
        self.bow = Bow(DEFAULT_BOW_X, self.bow_height, GROUND_Y)
        
        # Ball Entity
        self.ball = None
        self.reload_ball()
        
        # Target Entity (White Stick Figure)
        self.stick_figure = None
        self._spawn_stick_figure()
        
        # Register Collision Handlers (Pymunk 7+)
        self.space.on_collision(COLLISION_BALL, COLLISION_STICKMAN, post_solve=self._on_ball_hit_target)
        self.space.on_collision(COLLISION_BALL, COLLISION_GROUND, post_solve=self._on_ball_hit_ground)
        
        # Simulation States
        self.is_dragging = False
        self.game_completed = False
        self.screen_shake = 0.0
        self.particles = []
        
        # Telemetry Metrics
        self.initial_angle = 0.0
        self.initial_speed = 0.0
        
        # UI Elements
        self.telemetry = ui.TelemetryHUD(20, 80, 320, 215)
        self.banner = ui.GameCompletedBanner()
        self.settings_modal = None
        
        # Top HUD Buttons
        self.btn_menu = ui.Button(20, 16, 130, 48, "SETTINGS", self.open_menu, color_scheme="cyan", font_size=18)
        self.btn_reload = ui.Button(160, 16, 150, 48, "RELOAD BALL", self.reload_ball, color_scheme="default", font_size=17)
        self.btn_telemetry = ui.Button(320, 16, 150, 48, "TELEMETRY", self.toggle_telemetry, color_scheme="default", font_size=17)
        self.btn_main_menu = ui.Button(WIDTH - 160, 16, 140, 48, "MAIN MENU", 
                                       self.go_to_main_menu, color_scheme="default", font_size=17)

        # Game Completed Victory Overlay Button
        btn_w, btn_h = 200, 52
        self.victory_buttons = [
            ui.Button(WIDTH // 2 - btn_w - 10, 320, btn_w, btn_h, "SHOOT AGAIN", self.reset_simulation, color_scheme="green", font_size=19),
            ui.Button(WIDTH // 2 + 10, 320, btn_w, btn_h, "MAIN MENU", self.go_to_main_menu, color_scheme="default", font_size=19)
        ]
        self.defeat_buttons = []
        if self.level_id:
            self.victory_buttons = [
                ui.Button(WIDTH // 2 - btn_w - 10, 320, btn_w, btn_h, "REPLAY", self.reset_simulation, color_scheme="cyan", font_size=19),
                ui.Button(WIDTH // 2 + 10, 320, btn_w, btn_h, "NEXT LEVEL", self.next_level, color_scheme="green", font_size=19),
                ui.Button(WIDTH // 2 - btn_w // 2, 380, btn_w, btn_h, "MAIN MENU", self.go_to_main_menu, color_scheme="default", font_size=19)
            ]
            self.defeat_buttons = [
                ui.Button(WIDTH // 2 - btn_w - 10, 320, btn_w, btn_h, "RETRY", self.reset_simulation, color_scheme="cyan", font_size=19),
                ui.Button(WIDTH // 2 + 10, 320, btn_w, btn_h, "MAIN MENU", self.go_to_main_menu, color_scheme="default", font_size=19)
            ]

    def go_to_main_menu(self):
        """Returns to the main menu screen cleanly."""
        self.manager.change_state(menus.MainMenu(self.manager))


    def _spawn_stick_figure(self):
        """Creates or repositions the white stick figure target and obstacles."""
        if self.stick_figure:
            try:
                self.space.remove(self.stick_figure.body, *self.stick_figure.shapes)
            except (KeyError, ValueError):
                pass
        
        for obs in self.obstacles:
            try:
                self.space.remove(obs)
            except: pass
        self.obstacles = []
        
        target_x = self.bow.x + self.stickman_distance
        target_ground = getattr(self, 'target_ground', GROUND_Y)
        
        if self.level_data:
            for o_data in self.level_data["obstacles"]:
                if o_data["type"] == "platform":
                    obs = physics.create_obstacle(self.space, o_data["dist_m"], o_data["elev_m"], o_data["width_m"], 0.2, False, GROUND_Y)
                    self.obstacles.append(obs)
                elif o_data["type"] == "wall":
                    obs = physics.create_obstacle(self.space, o_data["dist_m"], 0, o_data["width_m"], o_data["height_m"], True, GROUND_Y)
                    self.obstacles.append(obs)
        
        self.target_base_x = target_x
        body, shapes = physics.create_stick_figure_target(self.space, target_x, target_ground, self.stickman_elasticity)
        self.stick_figure = StickFigure(body, shapes, target_ground)
        self.camera.update_targets(self.bow.x, self.bow.bow_y, target_x)

    def reload_ball(self):
        """Spawns or resets the red ball into the bow slingshot pouch."""
        if self.ball:
            try:
                self.space.remove(self.ball.body, self.ball.shape)
            except (KeyError, ValueError):
                pass
        
        rx, ry = self.bow.rest_pos
        body, shape = physics.create_ball(self.space, rx, ry, DEFAULT_BALL_RADIUS, self.ball_elasticity)
        body.velocity = (0.0, 0.0)
        body.angular_velocity = 0.0
        self.ball = Ball(body, shape, DEFAULT_BALL_RADIUS)
        self.ball.launched = False
        self.is_dragging = False

    
    def next_level(self):
        if self.level_id < 5:
            self.manager.change_state(PlayingState(self.manager, level_id=self.level_id + 1))
        else:
            self.go_to_main_menu()

    def reset_simulation(self):
        """Resets both ball and stick figure for another shot."""
        self.game_completed = False
        self.level_failed = False
        if self.level_id:
            self.attempts_left = self.max_attempts
        self._spawn_stick_figure()
        self.reload_ball()

    def open_menu(self):
        self.settings_modal = InGameSettingsModal(self)

    def close_menu(self):
        self.settings_modal = None

    def toggle_telemetry(self):
        self.telemetry.visible = not self.telemetry.visible

    # Physics Adjusters from Sliders
    def set_gravity(self, val):
        self.gravity_val = val
        self.space.gravity = (0.0, val * PIXELS_PER_METER)

    def set_ball_elasticity(self, val):
        self.ball_elasticity = val
        if self.ball and self.ball.shape:
            self.ball.set_elasticity(val)

    def set_ground_elasticity(self, val):
        self.ground_elasticity = val
        if self.ground_shape:
            self.ground_shape.elasticity = val

    def set_stickman_elasticity(self, val):
        self.stickman_elasticity = val
        if self.stick_figure:
            self.stick_figure.set_elasticity(val)

    def set_stickman_distance_m(self, val):
        self.stickman_distance_m = val
        self.stickman_distance = val * PIXELS_PER_METER
        self._spawn_stick_figure()
        self.camera.update_targets(self.bow.x, self.bow.bow_y, self.bow.x + self.stickman_distance)

    def set_stickman_distance(self, val):
        self.set_stickman_distance_m(val / PIXELS_PER_METER)

    def set_bow_elevation_m(self, val):
        self.bow_elevation_m = val
        self.bow_elevation = val * PIXELS_PER_METER
        self.bow_height = GROUND_Y - self.bow_elevation
        self.bow.bow_y = self.bow_height
        if self.ball and not self.ball.launched:
            self.ball.body.position = self.bow.rest_pos
        self.camera.update_targets(self.bow.x, self.bow.bow_y, self.bow.x + self.stickman_distance)

    def set_bow_elevation(self, val):
        self.set_bow_elevation_m(val / PIXELS_PER_METER)

    def set_bow_height(self, val):
        self.set_bow_elevation(GROUND_Y - val)

    # Collision Callbacks
    def _on_ball_hit_target(self, arbiter, space, data):
        """Triggered when the red ball collides with the white stick figure."""
        impulse = arbiter.total_impulse.length
        if not self.game_completed and not self.level_failed:
            self.game_completed = True
            if self.level_id:
                used_attempts = self.max_attempts - self.attempts_left
                stars = 3 if used_attempts == 1 else (2 if used_attempts == 2 else 1)
                score = stars * 1000 + self.attempts_left * 500
                save_manager.update_score(self.level_id, score, stars)
                if self.level_id < 5:
                    save_manager.unlock_level(self.level_id + 1)
            
            if self.sound_hit:
                self.sound_hit.play()
            self.stick_figure.on_hit(impulse)
            self.banner.reset()
            self.screen_shake = 10.0
            
            # Apply dynamic knockback force to stick figure
            if self.ball:
                vx, vy = self.ball.body.velocity
                knockback = (vx * 1.5, min(-100.0, vy * 1.2))
                self.stick_figure.body.apply_impulse_at_local_point(knockback, (0, -25))
                self.stick_figure.body.angular_velocity = random.uniform(3.0, 6.0) if vx > 0 else random.uniform(-6.0, -3.0)
            
            # Spawn burst of victory particles at collision point
            cp = arbiter.contact_point_set.points[0].point_a
            for _ in range(35):
                self.particles.append({
                    'x': cp.x,
                    'y': cp.y,
                    'vx': random.uniform(-200, 200),
                    'vy': random.uniform(-240, 40),
                    'life': 1.3,
                    'color': random.choice([COLOR_BALL_RED, COLOR_GREEN_ACCENT, COLOR_WHITE, COLOR_GOLD_ACCENT]),
                    'size': random.randint(3, 6)
                })
        return True

    def _on_ball_hit_ground(self, arbiter, space, data):
        """Triggered when the ball bounces off the ground."""
        impulse_len = arbiter.total_impulse.length
        if self.ball and impulse_len > 40:
            self.ball.bounces += 1
            if impulse_len > 300:
                cp = arbiter.contact_point_set.points[0].point_a
                for _ in range(4):
                    self.particles.append({
                        'x': cp.x,
                        'y': cp.y,
                        'vx': random.uniform(-60, 60),
                        'vy': random.uniform(-80, -10),
                        'life': 0.6,
                        'color': (80, 100, 130),
                        'size': 3
                    })
        return True

    def handle_events(self, events):
        for e in events:
            # If settings modal is open, forward events to it first
            if self.settings_modal:
                if self.settings_modal.handle_event(e):
                    continue

            # Top HUD buttons
            if self.btn_menu.handle_event(e): continue
            if self.btn_reload.handle_event(e): continue
            if self.btn_telemetry.handle_event(e): continue
            if self.btn_main_menu.handle_event(e): continue

            # Victory/Defeat buttons
            if self.game_completed:
                handled = False
                for vb in self.victory_buttons:
                    if vb.handle_event(e):
                        handled = True
                        break
                if handled: continue
            elif self.level_failed:
                handled = False
                for db in self.defeat_buttons:
                    if db.handle_event(e):
                        handled = True
                        break
                if handled: continue

            # Slingshot / Ball dragging interaction (converted from screen to world)
            rx, ry = self.bow.rest_pos
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.ball and not self.ball.launched:
                    mx, my = e.pos
                    wx, wy = self.camera.screen_to_world(mx, my)
                    if math.hypot(wx - self.ball.x, wy - self.ball.y) < 60:
                        self.is_dragging = True

            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if self.is_dragging and self.ball and not self.ball.launched:
                    self.is_dragging = False
                    dx = rx - self.ball.x
                    dy = ry - self.ball.y
                    dist = math.hypot(dx, dy)
                    
                    if dist > 10:
                        # Launch the ball!
                        self.ball.launched = True
                        if self.sound_throw:
                            self.sound_throw.play()
                        vx = dx * LAUNCH_POWER_MULTIPLIER
                        vy = dy * LAUNCH_POWER_MULTIPLIER
                        self.ball.body.velocity = (vx, vy)
                        
                        self.initial_angle = math.degrees(math.atan2(-vy, vx))
                        self.initial_speed = math.hypot(vx, vy) / PIXELS_PER_METER
                        self.ball.initial_velocity = (vx, vy)
                        self.ball.initial_angle = self.initial_angle
                        self.ball.launch_time = pygame.time.get_ticks()
                        if self.level_data:
                            self.attempts_left -= 1
                    else:
                        self.ball.body.position = (rx, ry)
                        self.ball.body.velocity = (0.0, 0.0)

            elif e.type == pygame.MOUSEMOTION:
                if self.is_dragging and self.ball and not self.ball.launched:
                    mx, my = e.pos
                    wx, wy = self.camera.screen_to_world(mx, my)
                    dx = wx - rx
                    dy = wy - ry
                    dist = math.hypot(dx, dy)
                    if dist > SLING_MAX_PULL:
                        angle = math.atan2(dy, dx)
                        wx = rx + math.cos(angle) * SLING_MAX_PULL
                        wy = ry + math.sin(angle) * SLING_MAX_PULL
                    self.ball.body.position = (wx, wy)
                    self.ball.body.velocity = (0.0, 0.0)

    def update(self, dt):
        # Update camera zoom and position
        target_x = self.bow.x + self.stickman_distance
        self.camera.update_targets(self.bow.x, self.bow.bow_y, target_x)
        self.camera.update(dt)

        if self.settings_modal:
            return  # Pause physics while settings menu is open

        # Hold pre-launch states steady
        if self.ball and not self.ball.launched:
            if not self.is_dragging:
                self.ball.body.position = self.bow.rest_pos
            self.ball.body.velocity = (0.0, 0.0)
            self.ball.body.angular_velocity = 0.0

        if self.stick_figure and not self.stick_figure.is_hit:
            target_ground = getattr(self, 'target_ground', GROUND_Y)
            if not getattr(self, 'moving_target', False):
                self.stick_figure.body.position = (target_x, target_ground - 55)
            else:
                self.stick_figure.body.position = (self.stick_figure.body.position.x, target_ground - 55)
            self.stick_figure.body.angle = 0.0
            self.stick_figure.body.velocity = (0.0, 0.0)
            self.stick_figure.body.angular_velocity = 0.0

        # Decay screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - dt * 25.0)
            
        if getattr(self, 'level_title_timer', 0) > 0:
            self.level_title_timer -= dt

        # Step Pymunk physics with sub-stepping for numerical precision
        for _ in range(PHYSICS_STEPS):
            self.space.step(dt / PHYSICS_STEPS)

        # Update entities
        if self.ball:
            self.ball.update(dt)
            # Check if settled or off screen
            if self.ball.launched and not self.game_completed and not self.level_failed:
                if self.ball.is_settled() or self.ball.x > WIDTH*5 or self.ball.x < -WIDTH:
                    if self.attempts_left <= 0:
                        self.level_failed = True
                    else:
                        self.reload_ball()
        
        if self.stick_figure:
            self.stick_figure.update(dt)
            if self.moving_target and not self.stick_figure.is_hit:
                speed = self.level_data["move_speed_m"] * PIXELS_PER_METER
                range_px = self.level_data["move_range_m"] * PIXELS_PER_METER
                new_x = self.stick_figure.body.position.x + speed * self.move_dir * dt
                if new_x > self.target_base_x + range_px:
                    self.move_dir = -1.0
                    new_x = self.target_base_x + range_px
                elif new_x < self.target_base_x - range_px:
                    self.move_dir = 1.0
                    new_x = self.target_base_x - range_px
                
                target_ground = getattr(self, 'target_ground', GROUND_Y)
                self.stick_figure.body.position = (new_x, target_ground - 55)

        # Update celebration banner
        if self.game_completed:
            self.banner.update(dt)

        # Update particle effects
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += 300 * dt
            p['life'] -= dt * 1.5
        self.particles = [p for p in self.particles if p['life'] > 0]

    def _draw_trajectory_dots(self, surface):
        """Draws dynamic predictive trajectory dots transformed by camera."""
        if self.is_dragging and self.ball and not self.ball.launched:
            rx, ry = self.bow.rest_pos
            dx = rx - self.ball.x
            dy = ry - self.ball.y
            vx = dx * LAUNCH_POWER_MULTIPLIER
            vy = dy * LAUNCH_POWER_MULTIPLIER
            
            points = self.bow.calculate_trajectory((self.ball.x, self.ball.y), (vx, vy), self.gravity_val)
            for i, (wx, wy) in enumerate(points):
                sx, sy = self.camera.world_to_screen(wx, wy)
                if -20 <= sx <= WIDTH + 20 and -20 <= sy <= HEIGHT + 20:
                    alpha = max(40, 255 - i * 7)
                    dot_size = max(2, int((6 - i // 6) * self.camera.zoom))
                    dot_surf = pygame.Surface((dot_size * 2, dot_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(dot_surf, (255, 255, 255, alpha), (dot_size, dot_size), dot_size)
                    surface.blit(dot_surf, (int(sx - dot_size), int(sy - dot_size)))

    def draw(self, surface):
        # Apply screen shake offset
        shake_x = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        sim_surf = pygame.Surface((WIDTH, HEIGHT))

        # 1. Dark environment background & fence (with camera framing)
        assets.draw_dark_background(sim_surf)
        assets.draw_fence(sim_surf, camera=self.camera)

        # 2. Bow Structure (Stand & Prongs)
        self.bow.draw_structure(sim_surf, camera=self.camera)

        # 3. Bow Elastic Strings
        if self.ball and not self.ball.launched:
            ball_pos = (self.ball.x, self.ball.y)
            self.bow.draw_bands_and_pouch(sim_surf, ball_pos, self.is_dragging, camera=self.camera)
        else:
            self.bow.draw_bands_and_pouch(sim_surf, self.bow.rest_pos, is_dragging=False, camera=self.camera)

        # 4. Trajectory Preview Dots
        self._draw_trajectory_dots(sim_surf)

        # 5. Draw Obstacles
        for obs in self.obstacles:
            if hasattr(obs, 'a') and hasattr(obs, 'b'):
                # It's a segment shape
                p1 = obs.a
                p2 = obs.b
                radius = obs.radius
                sx1, sy1 = self.camera.world_to_screen(p1.x, p1.y)
                sx2, sy2 = self.camera.world_to_screen(p2.x, p2.y)
                r_screen = radius * self.camera.zoom
                pygame.draw.line(sim_surf, (80, 80, 80), (sx1, sy1), (sx2, sy2), int(r_screen * 2))
                pygame.draw.circle(sim_surf, (80, 80, 80), (int(sx1), int(sy1)), int(r_screen))
                pygame.draw.circle(sim_surf, (80, 80, 80), (int(sx2), int(sy2)), int(r_screen))

        # 5. Stick Figure Target & Red Ball
        if self.stick_figure:
            self.stick_figure.draw(sim_surf, camera=self.camera)
        if self.ball:
            self.ball.draw(sim_surf, camera=self.camera)

        # 6. Solid Ground & Glowing Surface Line (Scale zeroed at the bow)
        assets.draw_ground(sim_surf, origin_x=self.bow.x, camera=self.camera)

        # 7. Particles
        for p in self.particles:
            alpha = max(0, min(255, int(255 * p['life'])))
            size = max(1, int(p.get('size', 3) * self.camera.zoom))
            sx, sy = self.camera.world_to_screen(p['x'], p['y'])
            if -20 <= sx <= WIDTH + 20 and -20 <= sy <= HEIGHT + 20:
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p['color'][:3], alpha), (size, size), size)
                sim_surf.blit(s, (int(sx - size), int(sy - size)))

        # Blit main scene with shake offset
        surface.blit(sim_surf, (shake_x, shake_y))

        # 8. Telemetry Scientific Overlay
        self.telemetry.draw(surface, self.gravity_val, self.ball, self.stick_figure, self.initial_angle, self.initial_speed)

        # 9. Top HUD Buttons
        self.btn_menu.draw(surface)
        self.btn_reload.draw(surface)
        self.btn_telemetry.draw(surface)
        self.btn_main_menu.draw(surface)

        # 10. Game Completed Static Banner & Victory Buttons
        if self.game_completed:
            self.banner.draw(surface)
            if self.level_id:
                font = assets.get_font(30, bold=True)
                used = self.max_attempts - self.attempts_left
                stars = 3 if used == 1 else (2 if used == 2 else 1)
                t_surf = font.render(f"Stars Earned: {stars}", True, COLOR_GOLD_ACCENT)
                surface.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, 260)))
            if self.level_id and self.level_id == 5:
                font = assets.get_font(40, bold=True)
                t_surf = font.render("ALL LEVELS COMPLETED!", True, COLOR_GOLD_ACCENT)
                surface.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, 280)))
            for vb in self.victory_buttons:
                vb.draw(surface)
        elif self.level_failed:
            font = assets.get_font(62, bold=True)
            t_surf = font.render("LEVEL FAILED", True, COLOR_RED_ACCENT)
            surface.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, 210)))
            for db in self.defeat_buttons:
                db.draw(surface)
                
        if self.level_id:
            font = assets.get_font(24, bold=True)
            txt = f"Level {self.level_id} | Attempts Left: {self.attempts_left}"
            surf = font.render(txt, True, COLOR_WHITE)
            surface.blit(surf, (WIDTH//2 - surf.get_width()//2, 20))
            
            # Fading level title
            if getattr(self, 'level_title_timer', 0) > 0:
                alpha = min(255, int(self.level_title_timer * 255))
                font_title = assets.get_font(50, bold=True)
                title_txt = f"Level {self.level_id} - {self.level_data['name']}"
                title_surf = font_title.render(title_txt, True, COLOR_CYAN_ACCENT)
                title_surf.set_alpha(alpha)
                surface.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))

        # 11. Floating Settings Modal (if opened)
        if self.settings_modal:
            self.settings_modal.draw(surface)
