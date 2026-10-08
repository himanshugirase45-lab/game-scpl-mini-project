import os

with open('state_machine.py', 'r', encoding='utf-8') as f:
    code = f.read()

draw_old = '''        # 10. Game Completed Static Banner & Victory Buttons
        if self.game_completed:
            self.banner.draw(surface)
            if self.level_id and self.level_id == 5:'''
draw_new = '''        # 10. Game Completed Static Banner & Victory Buttons
        if self.game_completed:
            self.banner.draw(surface)
            if self.level_id:
                font = assets.get_font(30, bold=True)
                used = self.max_attempts - self.attempts_left
                stars = 3 if used == 1 else (2 if used == 2 else 1)
                t_surf = font.render(f"Stars Earned: {stars}", True, COLOR_GOLD_ACCENT)
                surface.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, 260)))
            if self.level_id and self.level_id == 5:'''
code = code.replace(draw_old, draw_new)

with open('state_machine.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied state_machine.py stars changes")
