import os

with open('state_machine.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix 1: Initialize stickman_distance correctly in __init__ based on level_data
init_old = '''        self.stickman_elasticity = DEFAULT_STICKMAN_ELASTICITY
        self.stickman_distance_m = DEFAULT_STICKMAN_DISTANCE_M
        self.stickman_distance = DEFAULT_STICKMAN_DISTANCE'''
init_new = '''        self.stickman_elasticity = DEFAULT_STICKMAN_ELASTICITY
        self.stickman_distance_m = self.level_data["target_distance_m"] if self.level_data else DEFAULT_STICKMAN_DISTANCE_M
        self.stickman_distance = self.stickman_distance_m * PIXELS_PER_METER
        self.target_ground = GROUND_Y - (self.level_data["target_elevation_m"] * PIXELS_PER_METER if self.level_data else 0)'''
code = code.replace(init_old, init_new)

# Fix 2: Simplify _spawn_stick_figure since __init__ now sets distance properly
spawn_old = '''        target_x = self.bow.x + self.stickman_distance
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
        body, shapes = physics.create_stick_figure_target(self.space, target_x, target_ground, self.stickman_elasticity)'''

spawn_new = '''        target_x = self.bow.x + self.stickman_distance
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
        body, shapes = physics.create_stick_figure_target(self.space, target_x, target_ground, self.stickman_elasticity)'''
code = code.replace(spawn_old, spawn_new)

# Fix 3: update() resetting position
update_old = '''        if self.stick_figure and not self.stick_figure.is_hit:
            self.stick_figure.body.position = (target_x, GROUND_Y - 55)
            self.stick_figure.body.angle = 0.0
            self.stick_figure.body.velocity = (0.0, 0.0)
            self.stick_figure.body.angular_velocity = 0.0'''
update_new = '''        if self.stick_figure and not self.stick_figure.is_hit:
            target_ground = getattr(self, 'target_ground', GROUND_Y)
            if not getattr(self, 'moving_target', False):
                self.stick_figure.body.position = (target_x, target_ground - 55)
            else:
                self.stick_figure.body.position = (self.stick_figure.body.position.x, target_ground - 55)
            self.stick_figure.body.angle = 0.0
            self.stick_figure.body.velocity = (0.0, 0.0)
            self.stick_figure.body.angular_velocity = 0.0'''
code = code.replace(update_old, update_new)

# Fix moving target update to not be overridden
update_move_old = '''        if self.stick_figure:
            self.stick_figure.update(dt)
            if self.moving_target and not self.stick_figure.is_hit:
                speed = self.level_data["move_speed_m"] * PIXELS_PER_METER
                range_px = self.level_data["move_range_m"] * PIXELS_PER_METER
                new_x = self.stick_figure.body.position.x + speed * self.move_dir * dt
                if new_x > self.target_base_x + range_px:
                    self.move_dir = -1.0
                elif new_x < self.target_base_x - range_px:
                    self.move_dir = 1.0
                self.stick_figure.body.position = (new_x, self.stick_figure.body.position.y)'''

update_move_new = '''        if self.stick_figure:
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
                self.stick_figure.body.position = (new_x, target_ground - 55)'''
code = code.replace(update_move_old, update_move_new)

with open('state_machine.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed state_machine.py overriding target position.")
