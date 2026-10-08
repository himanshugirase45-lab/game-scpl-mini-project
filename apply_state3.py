import os

with open('state_machine.py', 'r', encoding='utf-8') as f:
    code = f.read()

draw_old = '''        # 10. Game Completed Static Banner & Victory Buttons
        if self.game_completed:
            self.banner.draw(surface)
            for vb in self.victory_buttons:
                vb.draw(surface)'''
draw_new = '''        # 10. Game Completed Static Banner & Victory Buttons
        if self.game_completed:
            self.banner.draw(surface)
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
            txt = f"Level {self.level_id}: {self.level_data['name']} | Attempts Left: {self.attempts_left}"
            surf = font.render(txt, True, COLOR_WHITE)
            surface.blit(surf, (WIDTH//2 - surf.get_width()//2, 20))'''
code = code.replace(draw_old, draw_new)

with open('state_machine.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied state_machine.py phase 3 changes")
