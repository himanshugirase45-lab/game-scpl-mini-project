"""
SCPL Simulation - Game Entities
Defines the Red Ball, White Stick Figure Target, and Bow (Slingshot) structures with camera support.
"""
import pygame
import pymunk
import math
from config import *
import assets

class Ball:
    def __init__(self, body, shape, radius=DEFAULT_BALL_RADIUS):
        self.body = body
        self.shape = shape
        self.radius = radius
        self.launched = False
        self.dragging = False
        self.trail = []          # List of (x, y) coordinates for motion blur trail
        self.bounces = 0
        self.launch_time = 0
        self.initial_velocity = (0.0, 0.0)
        self.initial_angle = 0.0 # Launch angle in degrees

    @property
    def x(self):
        return self.body.position.x

    @property
    def y(self):
        return self.body.position.y

    @property
    def speed_mps(self):
        """Current speed in meters per second."""
        if not self.launched:
            return 0.0
        spd = self.body.velocity.length / PIXELS_PER_METER
        return spd if spd >= 0.05 else 0.0

    @property
    def kinetic_energy(self):
        """Kinetic Energy E_k = 1/2 * m * v^2 in Joules."""
        if not self.launched:
            return 0.0
        v = self.speed_mps
        if v < 0.05:
            return 0.0
        return 0.5 * self.body.mass * (v ** 2)

    @property
    def height_meters(self):
        """Height above the ground in meters."""
        px_above_ground = max(0.0, GROUND_Y - self.y)
        return px_above_ground / PIXELS_PER_METER

    def update(self, dt):
        """Records motion trail and updates ball state."""
        if self.launched and self.body.body_type == pymunk.Body.DYNAMIC:
            # Append trail point every frame if moving
            if self.body.velocity.length > 20:
                self.trail.append((int(self.x), int(self.y)))
                if len(self.trail) > 28:
                    self.trail.pop(0)

    def is_settled(self, velocity_threshold=8.0):
        """Checks if the ball has come to a near complete rest."""
        if not self.launched or self.body.body_type != pymunk.Body.DYNAMIC:
            return False
        return self.body.velocity.length < velocity_threshold and abs(self.body.angular_velocity) < 0.8

    def set_elasticity(self, elasticity):
        self.shape.elasticity = elasticity

    def draw(self, surface, camera=None):
        zoom = camera.zoom if camera else 1.0
        
        # Draw fading motion trail
        trail_len = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            if camera:
                stx, sty = camera.world_to_screen(tx, ty)
            else:
                stx, sty = tx, ty
            alpha = max(0, min(255, int(140 * (i + 1) / trail_len)))
            r = max(2, int(self.radius * zoom * (i + 1) / (trail_len * 1.5)))
            trail_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*COLOR_BALL_TRAIL, alpha), (r, r), r)
            surface.blit(trail_surf, (int(stx - r), int(sty - r)))

        # Draw red ball
        assets.draw_red_ball(surface, self.x, self.y, self.radius, camera=camera)


class StickFigure:
    def __init__(self, body, shapes, ground_y=GROUND_Y):
        self.body = body
        self.shapes = shapes
        self.ground_y = ground_y
        self.is_hit = False
        self.hit_timer = 0.0
        self.impact_speed = 0.0

    @property
    def x(self):
        return self.body.position.x

    @property
    def y(self):
        return self.body.position.y

    def set_elasticity(self, elasticity):
        for shape in self.shapes:
            shape.elasticity = elasticity

    def on_hit(self, impact_force=0.0):
        """Called upon ball collision."""
        self.is_hit = True
        self.impact_speed = impact_force

    def update(self, dt):
        if self.is_hit:
            self.hit_timer += dt

    def draw(self, surface, camera=None):
        assets.draw_white_stick_figure(surface, self.body, is_hit=self.is_hit, ground_y=self.ground_y, camera=camera)


class Bow:
    def __init__(self, x=DEFAULT_BOW_X, bow_y=DEFAULT_BOW_HEIGHT, ground_y=GROUND_Y):
        self.x = x
        self.bow_y = bow_y
        self.ground_y = ground_y
        self.fork_h = 45
        self.prong_spread = 32

    @property
    def rest_pos(self):
        """Position where the ball rests before pulling."""
        return (self.x, self.bow_y - 22)

    @property
    def left_tip(self):
        return (self.x - self.prong_spread, self.bow_y - self.fork_h)

    @property
    def right_tip(self):
        return (self.x + self.prong_spread, self.bow_y - self.fork_h)

    def draw_bands_and_pouch(self, surface, ball_pos, is_dragging=False, camera=None):
        """
        Draws elastic slingshot / bow strings from both tips to the ball pouch.
        """
        zoom = camera.zoom if camera else 1.0
        
        def to_screen(wx, wy):
            return camera.world_to_screen(wx, wy) if camera else (wx, wy)

        bx, by = to_screen(ball_pos[0], ball_pos[1])
        lt = to_screen(self.left_tip[0], self.left_tip[1])
        rt = to_screen(self.right_tip[0], self.right_tip[1])

        band_w = max(2, int(4 * zoom))

        # Left elastic band
        pygame.draw.line(surface, COLOR_BOW_STRING, lt, (bx - 6 * zoom, by), band_w)
        # Right elastic band
        pygame.draw.line(surface, COLOR_BOW_STRING, rt, (bx + 6 * zoom, by), band_w)

        if is_dragging:
            # Leather pouch wrapping the ball
            pouch_w = max(8, int(24 * zoom))
            pouch_h = max(6, int(16 * zoom))
            pouch_rect = pygame.Rect(int(bx - pouch_w // 2), int(by - pouch_h // 2), pouch_w, pouch_h)
            pygame.draw.rect(surface, COLOR_BOW_POUCH, pouch_rect, border_radius=max(2, int(4 * zoom)))
            pygame.draw.rect(surface, (80, 50, 30), pouch_rect, max(1, int(2 * zoom)), border_radius=max(2, int(4 * zoom)))

    def draw_structure(self, surface, camera=None):
        """Renders the wooden/metal bow support structure."""
        assets.draw_bow_structure(surface, self.x, self.bow_y, self.ground_y, camera=camera)

    def calculate_trajectory(self, start_pos, velocity, gravity_val, steps=35, dt=0.06):
        """
        Calculates parabolic trajectory coordinates using standard kinematics:
        x(t) = x0 + vx * t
        y(t) = y0 + vy * t + 0.5 * g * t^2
        """
        points = []
        x0, y0 = start_pos
        vx, vy = velocity
        g_px = gravity_val * PIXELS_PER_METER

        for i in range(1, steps + 1):
            t = i * dt
            px = x0 + vx * t
            py = y0 + vy * t + 0.5 * g_px * (t ** 2)
            
            # Stop trajectory prediction at ground
            if py >= GROUND_Y:
                points.append((px, GROUND_Y))
                break
            points.append((px, py))

        return points
