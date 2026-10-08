import os
import re

# physics.py modification
with open('physics.py', 'r') as f:
    physics_code = f.read()

obstacle_code = '''
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
'''
if 'create_obstacle' not in physics_code:
    physics_code += obstacle_code
    with open('physics.py', 'w') as f:
        f.write(physics_code)

print("Applied physics.py changes")
