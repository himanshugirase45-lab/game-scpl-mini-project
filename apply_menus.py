import os

with open('menus.py', 'r', encoding='utf-8') as f:
    menus_code = f.read()

# Add LevelSelect import
if 'from level import LEVEL_CONFIG' not in menus_code:
    menus_code = menus_code.replace('import ui', 'import ui\nfrom level import LEVEL_CONFIG\nimport save_manager')

# Add LEVEL SELECT button to MainMenu
if 'LEVEL SELECT' not in menus_code:
    old_buttons = '''self.buttons = [
            ui.Button(center_x, start_y, btn_w, btn_h, "PLAY SIMULATION", 
                      self.start_game, color_scheme="green", font_size=22),
            ui.Button(center_x, start_y + spacing, btn_w, btn_h, "HOW TO PLAY", 
                      self.open_how_to_play, color_scheme="cyan", font_size=20),
            ui.Button(center_x, start_y + spacing * 2, btn_w, btn_h, "ABOUT GAME & PHYSICS", 
                      self.open_about_game, color_scheme="default", font_size=18),
            ui.Button(center_x, start_y + spacing * 3, btn_w, btn_h, "EXIT", 
                      self.manager.quit, color_scheme="red", font_size=20)
        ]'''
    
    new_buttons = '''self.buttons = [
            ui.Button(center_x, start_y, btn_w, btn_h, "LEVEL SELECT", 
                      self.open_level_select, color_scheme="green", font_size=22),
            ui.Button(center_x, start_y + spacing, btn_w, btn_h, "FREE SIMULATION", 
                      self.start_game, color_scheme="cyan", font_size=20),
            ui.Button(center_x, start_y + spacing * 2, btn_w, btn_h, "HOW TO PLAY", 
                      self.open_how_to_play, color_scheme="default", font_size=18),
            ui.Button(center_x, start_y + spacing * 3, btn_w, btn_h, "EXIT", 
                      self.manager.quit, color_scheme="red", font_size=20)
        ]'''
    menus_code = menus_code.replace(old_buttons, new_buttons)
    
    menus_code = menus_code.replace('def start_game(self):', 'def open_level_select(self):\n        self.manager.change_state(LevelSelect(self.manager))\n\n    def start_game(self):')

level_select_class = '''
class LevelSelect(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.save_data = save_manager.load_save()
        
        self.btn_back = ui.Button(20, 20, 150, 50, "BACK", 
                      lambda: self.manager.change_state(MainMenu(self.manager)), color_scheme="default")
        
        self.level_buttons = []
        start_x = 100
        start_y = 150
        spacing_x = 220
        spacing_y = 200
        
        for i, (lvl_id, lvl_data) in enumerate(LEVEL_CONFIG.items()):
            x = start_x + (i % 5) * spacing_x
            y = start_y + (i // 5) * spacing_y
            
            unlocked = self.save_data['levels'].get(str(lvl_id), {}).get('unlocked', False)
            if lvl_id == 1: unlocked = True # Level 1 always unlocked
            
            stars = self.save_data['levels'].get(str(lvl_id), {}).get('stars', 0)
            score = self.save_data['levels'].get(str(lvl_id), {}).get('score', 0)
            
            def make_action(l_id=lvl_id):
                return lambda: self.start_level(l_id)
            
            action = make_action() if unlocked else None
            scheme = "green" if unlocked else "red"
            text = f"Level {lvl_id}\\n{lvl_data['name']}\\n" + ("Locked" if not unlocked else f"Stars: {stars}")
            
            btn = ui.Button(x, y, 200, 150, text, action=action, color_scheme=scheme, font_size=16)
            self.level_buttons.append(btn)

    def start_level(self, level_id):
        from state_machine import PlayingState
        self.manager.change_state(PlayingState(self.manager, level_id=level_id))

    def handle_events(self, events):
        for e in events:
            self.btn_back.handle_event(e)
            for b in self.level_buttons:
                b.handle_event(e)

    def draw(self, surface):
        assets.draw_dark_background(surface)
        assets.draw_fence(surface)
        assets.draw_ground(surface)
        
        f_title = assets.get_font(48, bold=True)
        t_surf = f_title.render("SELECT LEVEL", True, COLOR_CYAN_ACCENT)
        surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 40))
        
        self.btn_back.draw(surface)
        for b in self.level_buttons:
            b.draw(surface)
'''
if 'class LevelSelect(GameState):' not in menus_code:
    menus_code += level_select_class

with open('menus.py', 'w', encoding='utf-8') as f:
    f.write(menus_code)

print("Applied menus.py changes")
