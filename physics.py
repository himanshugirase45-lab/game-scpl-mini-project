"""
SCPL Simulation - Physics Engine Integration (Pymunk)
Handles physics space creation, rigid body definitions for the red ball,
ground, boundaries, and white stick figure target with customizable restitution (elasticity).
"""
import pymunk
from config import *

def create_physics_space(gravity_val=DEFAULT_GRAVITY):
    """
    Initializes and configures the Pymunk 2D physics simulation space.
    gravity_val: Gravity in m/s^2 (default 9.8 m/s^2).
    """
    space = pymunk.Space()
    # Convert m/s^2 to pixels/s^2
    space.gravity = (0.0, gravity_val * PIXELS_PER_METER)
    space.damping = 0.998  # Very low air resistance
    space.collision_slop = 0.05
    return space

def create_ground(space, width=WIDTH, height=HEIGHT, ground_y=GROUND_Y, elasticity=DEFAULT_GROUND_ELASTICITY):
    """
    Creates static ground and boundary walls across a vast continuous space.
    """
    static_body = space.static_body
    
    # Solid ground segment extending vast distance in world space (-5000 to +200000 px)
    ground_shape = pymunk.Segment(static_body, (-5000, ground_y), (200000, ground_y), 5.0)
    ground_shape.elasticity = elasticity
    ground_shape.friction = 0.85
    ground_shape.collision_type = COLLISION_GROUND
    space.add(ground_shape)
    
    # Far left wall (well behind the bow)
    wall_left = pymunk.Segment(static_body, (-3000, -50000), (-3000, ground_y + 1000), 5.0)
    wall_left.elasticity = 0.6
    wall_left.friction = 0.5
    wall_left.collision_type = COLLISION_WALL
    
    # Far right wall (vast downfield buffer at x = 200,000 px)
    wall_right = pymunk.Segment(static_body, (200000, -50000), (200000, ground_y + 1000), 5.0)
    wall_right.elasticity = 0.6
    wall_right.friction = 0.5
    wall_right.collision_type = COLLISION_WALL
    
    space.add(wall_left, wall_right)
    return ground_shape

def create_ball(space, x, y, radius=DEFAULT_BALL_RADIUS, elasticity=DEFAULT_BALL_ELASTICITY, mass=DEFAULT_BALL_MASS):
    """
    Creates the dynamic red ball body and circular collision shape.
    """
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = (x, y)
    
    shape = pymunk.Circle(body, radius)
    shape.elasticity = elasticity
    shape.friction = 0.7
    shape.collision_type = COLLISION_BALL
    
    space.add(body, shape)
    return body, shape

def create_stick_figure_target(space, x, ground_y=GROUND_Y, elasticity=DEFAULT_STICKMAN_ELASTICITY):
    """
    Creates a composite multi-segment physical body for the white stick figure.
    Composed of head, torso, arms, and legs.
    """
    mass = 8.0  # kg
    # Center of mass is around mid-torso (~55 px above ground)
    target_center_y = ground_y - 55
    moment = pymunk.moment_for_box(mass, (30, 110))
    
    body = pymunk.Body(mass, moment)
    body.position = (x, target_center_y)
    
    # Local coordinate shapes relative to center of mass
    shapes = []
    
    # 1. Head circle (radius 14, at top: -38)
    head_shape = pymunk.Circle(body, 14, (0, -38))
    head_shape.elasticity = elasticity
    head_shape.friction = 0.8
    head_shape.collision_type = COLLISION_STICKMAN
    shapes.append(head_shape)
    
    # 2. Torso segment (-24 to +15)
    torso_shape = pymunk.Segment(body, (0, -24), (0, 15), 6)
    torso_shape.elasticity = elasticity
    torso_shape.friction = 0.8
    torso_shape.collision_type = COLLISION_STICKMAN
    shapes.append(torso_shape)
    
    # 3. Left & Right Legs (+15 to +50)
    leg_left = pymunk.Segment(body, (0, 15), (-12, 50), 5)
    leg_left.elasticity = elasticity
    leg_left.friction = 0.9
    leg_left.collision_type = COLLISION_STICKMAN
    shapes.append(leg_left)
    
    leg_right = pymunk.Segment(body, (0, 15), (12, 50), 5)
    leg_right.elasticity = elasticity
    leg_right.friction = 0.9
    leg_right.collision_type = COLLISION_STICKMAN
    shapes.append(leg_right)
    
    # 4. Arms
    arm_left = pymunk.Segment(body, (0, -18), (-16, 12), 4)
    arm_left.elasticity = elasticity
    arm_left.collision_type = COLLISION_STICKMAN
    shapes.append(arm_left)
    
    arm_right = pymunk.Segment(body, (0, -18), (16, 12), 4)
    arm_right.elasticity = elasticity
    arm_right.collision_type = COLLISION_STICKMAN
    shapes.append(arm_right)
    
    space.add(body, *shapes)
    return body, shapes

def create_obstacle(space, dist_m, elev_m, width_m, height_m, is_wall=False, ground_y=GROUND_Y):
    body = space.static_body
    width_px = width_m * PIXELS_PER_METER
    height_px = height_m * PIXELS_PER_METER
    x = DEFAULT_BOW_X + dist_m * PIXELS_PER_METER
    
    if is_wall:
        y_bottom = ground_y
        y_top = ground_y - height_px
        shape = pymunk.Segment(body, (x, y_bottom), (x, y_top), width_px / 2.0)
    else:
        y = ground_y - elev_m * PIXELS_PER_METER
        shape = pymunk.Segment(body, (x - width_px/2, y), (x + width_px/2, y), height_px / 2.0)
        
    shape.elasticity = 0.5
    shape.friction = 0.8
    shape.collision_type = COLLISION_WALL
    space.add(shape)
    return shape
