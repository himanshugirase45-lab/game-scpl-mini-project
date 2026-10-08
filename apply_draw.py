import os

with open('state_machine.py', 'r', encoding='utf-8') as f:
    code = f.read()

draw_old = '''        # 5. Stick Figure Target & Red Ball
        if self.stick_figure:
            self.stick_figure.draw(sim_surf, camera=self.camera)
        if self.ball:
            self.ball.draw(sim_surf, camera=self.camera)'''

draw_new = '''        # 5. Draw Obstacles
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
            self.ball.draw(sim_surf, camera=self.camera)'''

code = code.replace(draw_old, draw_new)

with open('state_machine.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Added obstacle rendering.")
