import pygame
import sys
from main import main as start_chess_game

# --- Configuration ---
WIDTH, HEIGHT = 512, 512
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 200, 0)

def draw_text(screen, text, size, x, y, color=BLACK):
    font = pygame.font.SysFont("Arial", size, True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Launcher")
    clock = pygame.time.Clock()

    # Define Button
    button_width, button_height = 200, 60
    button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2), (button_width, button_height))

    while True:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(mouse_pos):
                    # Launch the actual game
                    start_chess_game() 

        # Draw UI
        draw_text(screen, "PYTHON CHESS", 48, WIDTH//2, HEIGHT//3)
        
        # Hover effect
        color = GREEN if button_rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        draw_text(screen, "PLAY", 32, WIDTH//2, HEIGHT//2 + 30, WHITE)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main_menu()