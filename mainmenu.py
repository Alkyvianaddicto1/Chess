import pygame
import sys
from main import main as start_chess_game

# --- Configuration ---
WIDTH, HEIGHT = 512, 512
WHITE = (240, 240, 240)
BLACK = (30, 30, 30)
GRAY = (100, 100, 100)
GREEN = (46, 139, 87)
RED = (178, 34, 34)

def draw_text(screen, text, size, x, y, color=BLACK):
    font = pygame.font.SysFont("Segoe UI", size, True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Launcher")
    clock = pygame.time.Clock()

    # Button Dimensions
    btn_w, btn_h = 200, 50
    play_btn = pygame.Rect(WIDTH//2 - btn_w//2, 250, btn_w, btn_h)
    quit_btn = pygame.Rect(WIDTH//2 - btn_w//2, 320, btn_w, btn_h)

    while True:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(mouse_pos):
                    # This runs the game. When the game ends, it returns here.
                    start_chess_game() 
                if quit_btn.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        # Title
        draw_text(screen, "PYTHON CHESS", 52, WIDTH//2, 150, BLACK)
        
        # Play Button
        play_color = GREEN if play_btn.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, play_color, play_btn, border_radius=8)
        draw_text(screen, "PLAY GAME", 24, WIDTH//2, 275, WHITE)

        # Quit Button
        quit_color = RED if quit_btn.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, quit_color, quit_btn, border_radius=8)
        draw_text(screen, "QUIT", 24, WIDTH//2, 345, WHITE)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main_menu()