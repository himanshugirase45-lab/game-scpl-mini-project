import os

with open('state_machine.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Disable settings button if level mode
btn_menu_old = '''self.btn_menu = ui.Button(20, 16, 130, 48, "SETTINGS", self.open_menu, color_scheme="cyan", font_size=18)'''
btn_menu_new = '''self.btn_menu = ui.Button(20, 16, 130, 48, "SETTINGS", self.open_menu, color_scheme="cyan", font_size=18)
        if self.level_id:
            self.btn_menu = ui.Button(20, 16, 130, 48, "LOCKED", None, color_scheme="red", font_size=18)'''
code = code.replace(btn_menu_old, btn_menu_new)

# Handle Victory UI and Level unlock
victory_old = '''        # Game Completed Victory Overlay Button (Only SHOOT AGAIN)
        btn_w, btn_h = 200, 52
        self.victory_buttons = [
            ui.Button(WIDTH // 2 - btn_w // 2, 285, btn_w, btn_h, "SHOOT AGAIN", self.reset_simulation, color_scheme="green", font_size=19)
        ]'''

victory_new = '''        # Game Completed Victory Overlay Button
        btn_w, btn_h = 200, 52
        self.victory_buttons = [
            ui.Button(WIDTH // 2 - btn_w // 2, 285, btn_w, btn_h, "SHOOT AGAIN", self.reset_simulation, color_scheme="green", font_size=19)
        ]
        self.defeat_buttons = []
        if self.level_id:
            from menus import LevelSelect, MainMenu
            self.victory_buttons = [
                ui.Button(WIDTH // 2 - btn_w - 10, 320, btn_w, btn_h, "REPLAY", self.reset_simulation, color_scheme="cyan", font_size=19),
                ui.Button(WIDTH // 2 + 10, 320, btn_w, btn_h, "NEXT LEVEL", self.next_level, color_scheme="green", font_size=19),
                ui.Button(WIDTH // 2 - btn_w // 2, 380, btn_w, btn_h, "MAIN MENU", lambda: self.manager.change_state(MainMenu(self.manager)), color_scheme="default", font_size=19)
            ]
            self.defeat_buttons = [
                ui.Button(WIDTH // 2 - btn_w - 10, 320, btn_w, btn_h, "RETRY", self.reset_simulation, color_scheme="cyan", font_size=19),
                ui.Button(WIDTH // 2 + 10, 320, btn_w, btn_h, "MAIN MENU", lambda: self.manager.change_state(MainMenu(self.manager)), color_scheme="default", font_size=19)
            ]
'''
code = code.replace(victory_old, victory_new)

# Add next_level method
next_lvl = '''
    def next_level(self):
        if self.level_id < 5:
            self.manager.change_state(PlayingState(self.manager, level_id=self.level_id + 1))
        else:
            from menus import MainMenu
            self.manager.change_state(MainMenu(self.manager))
'''
code = code.replace('def reset_simulation(self):', next_lvl + '\n    def reset_simulation(self):')

# Reset simulation logic update
reset_old = '''    def reset_simulation(self):
        """Resets both ball and stick figure for another shot."""
        self.game_completed = False
        self._spawn_stick_figure()
        self.reload_ball()'''
reset_new = '''    def reset_simulation(self):
        """Resets both ball and stick figure for another shot."""
        self.game_completed = False
        self.level_failed = False
        if self.level_id:
            self.attempts_left = self.max_attempts
        self._spawn_stick_figure()
        self.reload_ball()'''
code = code.replace(reset_old, reset_new)

# Event handler for defeat and victory buttons
evt_old = '''            # Victory buttons if game completed
            if self.game_completed:
                handled = False
                for vb in self.victory_buttons:
                    if vb.handle_event(e):
                        handled = True
                        break
                if handled:
                    continue'''
evt_new = '''            # Victory/Defeat buttons
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
                if handled: continue'''
code = code.replace(evt_old, evt_new)

# Hit target logic -> calculate stars and save
hit_old = '''        impulse = arbiter.total_impulse.length
        if not self.game_completed:
            self.game_completed = True
            if self.sound_hit:
                self.sound_hit.play()'''
hit_new = '''        impulse = arbiter.total_impulse.length
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
                self.sound_hit.play()'''
code = code.replace(hit_old, hit_new)


with open('state_machine.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied state_machine.py phase 2 changes")
