import pygame
import sys

# --- Configuration ---
WIDTH, HEIGHT = 712, 512
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Select Game Mode")
font = pygame.font.SysFont("Arial", 30, True)

def draw_button(text, y_pos, color, hover_color):
    mouse = pygame.mouse.get_pos()
    button_rect = pygame.Rect(WIDTH // 2 - 150, y_pos, 300, 60)
    current_color = hover_color if button_rect.collidepoint(mouse) else color
    pygame.draw.rect(screen, current_color, button_rect, border_radius=10)
    text_surf = font.render(text, True, pygame.Color("white"))
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    return button_rect

def mode_menu():
    while True:
        screen.fill((30, 30, 30))
        title_surf = font.render("CHOOSE YOUR CHALLENGE", True, pygame.Color("lightgray"))
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 50))

        pvp_btn = draw_button("Player vs Player", 130, (50, 100, 50), (70, 150, 70))
        
        # Difficulty Buttons
        easy_btn = draw_button("Computer: Easy", 210, (100, 50, 50), (150, 70, 70))
        med_btn = draw_button("Computer: Medium", 290, (100, 50, 50), (150, 70, 70))
        hard_btn = draw_button("Computer: Hard", 370, (100, 50, 50), (150, 70, 70))
        god_btn = draw_button("Computer: God Mode", 450, (139, 0, 0), (255, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_btn.collidepoint(event.pos): return "PVP"
                if easy_btn.collidepoint(event.pos): return "EASY"
                if med_btn.collidepoint(event.pos): return "MEDIUM"
                if hard_btn.collidepoint(event.pos): return "HARD"
                if god_btn.collidepoint(event.pos): return "GOD MODE"

        pygame.display.flip()