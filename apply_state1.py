import os

with open('state_machine.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add imports
if 'import save_manager' not in code:
    code = code.replace('import physics', 'import physics\nimport save_manager\nfrom level import LEVEL_CONFIG')

# Modify PlayingState __init__
init_old = '''    def __init__(self, manager):
        super().__init__(manager)'''

init_new = '''    def __init__(self, manager, level_id=None):
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
'''
code = code.replace(init_old, init_new)

# Modify _spawn_stick_figure
spawn_old = '''    def _spawn_stick_figure(self):
        """Creates or repositions the white stick figure target."""
        if self.stick_figure:
            try:
                self.space.remove(self.stick_figure.body, *self.stick_figure.shapes)
            except (KeyError, ValueError):
                pass
        target_x = self.bow.x + self.stickman_distance
        body, shapes = physics.create_stick_figure_target(self.space, target_x, GROUND_Y, self.stickman_elasticity)
        self.stick_figure = StickFigure(body, shapes, GROUND_Y)
        self.camera.update_targets(self.bow.x, self.bow.bow_y, target_x)'''

spawn_new = '''    def _spawn_stick_figure(self):
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
        target_ground = GROUND_Y
        
        if self.level_data:
            target_x = self.bow.x + self.level_data["target_distance_m"] * PIXELS_PER_METER
            target_ground = GROUND_Y - self.level_data["target_elevation_m"] * PIXELS_PER_METER
            
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
        self.camera.update_targets(self.bow.x, self.bow.bow_y, target_x)'''
code = code.replace(spawn_old, spawn_new)

# Modify update to handle attempts and moving target
update_old = '''        # Update entities
        if self.ball:
            self.ball.update(dt)
        if self.stick_figure:
            self.stick_figure.update(dt)

        # Update celebration banner'''

update_new = '''        # Update entities
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
                elif new_x < self.target_base_x - range_px:
                    self.move_dir = 1.0
                self.stick_figure.body.position = (new_x, self.stick_figure.body.position.y)

        # Update celebration banner'''
code = code.replace(update_old, update_new)

# Launch logic attempt deduction
launch_old = '''                        self.initial_angle = math.degrees(math.atan2(-vy, vx))
                        self.initial_speed = math.hypot(vx, vy) / PIXELS_PER_METER
                        self.ball.initial_velocity = (vx, vy)
                        self.ball.initial_angle = self.initial_angle
                        self.ball.launch_time = pygame.time.get_ticks()'''
                        
launch_new = '''                        self.initial_angle = math.degrees(math.atan2(-vy, vx))
                        self.initial_speed = math.hypot(vx, vy) / PIXELS_PER_METER
                        self.ball.initial_velocity = (vx, vy)
                        self.ball.initial_angle = self.initial_angle
                        self.ball.launch_time = pygame.time.get_ticks()
                        if self.level_data:
                            self.attempts_left -= 1'''
code = code.replace(launch_old, launch_new)

with open('state_machine.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied state_machine.py phase 1 changes")
