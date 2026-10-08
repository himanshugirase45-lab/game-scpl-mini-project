import os

with open('state_machine.py', 'r', encoding='utf-8') as f:
    code = f.read()

init_old = '''        self.target_base_x = 0'''
init_new = '''        self.target_base_x = 0
        self.level_title_timer = 3.0'''
code = code.replace(init_old, init_new)

update_old = '''        # Decay screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - dt * 25.0)'''
update_new = '''        # Decay screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - dt * 25.0)
            
        if getattr(self, 'level_title_timer', 0) > 0:
            self.level_title_timer -= dt'''
code = code.replace(update_old, update_new)

draw_old = '''        if self.level_id:
            font = assets.get_font(24, bold=True)
            txt = f"Level {self.level_id}: {self.level_data['name']} | Attempts Left: {self.attempts_left}"
            surf = font.render(txt, True, COLOR_WHITE)
            surface.blit(surf, (WIDTH//2 - surf.get_width()//2, 20))'''
draw_new = '''        if self.level_id:
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
                surface.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))'''
code = code.replace(draw_old, draw_new)

with open('state_machine.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Added title banner.")
