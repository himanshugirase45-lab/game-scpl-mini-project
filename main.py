"""
SCPL Simulation - Main Application Entry Point
Scientific Computing in Python: Projectile Motion & Physics Simulation
"""
import pygame
import sys
from config import *
from menus import MainMenu

def main():
    pygame.init()
    pygame.font.init()
    
    # Set Window Caption & Custom Icon
    pygame.display.set_caption("SCPL Projectile Simulation")
    try:
        icon_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(icon_surf, COLOR_BALL_RED, (16, 16), 14)
        pygame.draw.circle(icon_surf, COLOR_BALL_SHINE, (11, 11), 4)
        pygame.display.set_icon(icon_surf)
    except Exception:
        pass
    
    # Create main display surface
    flags = pygame.SCALED | pygame.RESIZABLE
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    clock = pygame.time.Clock()

    class GameManager:
        def __init__(self):
            self.state = MainMenu(self)
            self.running = True

        def change_state(self, new_state):
            self.state = new_state

        def quit(self):
            self.running = False

        def run(self):
            while self.running:
                dt = clock.tick(FPS) / 1000.0
                events = pygame.event.get()
                for e in events:
                    if e.type == pygame.QUIT:
                        self.quit()

                self.state.handle_events(events)
                self.state.update(dt)
                self.state.draw(screen)
                pygame.display.flip()

    game = GameManager()
    game.run()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
