import pygame
import sys

# --- Configuration ---
WIDTH, HEIGHT = 712, 512 # Matches your BOARD_WIDTH + PANEL_WIDTH
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Select Game Mode")
font = pygame.font.SysFont("Arial", 30, True)

def draw_button(text, y_pos, color, hover_color):
    mouse = pygame.mouse.get_pos()
    button_rect = pygame.Rect(WIDTH // 2 - 150, y_pos, 300, 60)
    
    # Hover effect
    current_color = hover_color if button_rect.collidepoint(mouse) else color
    pygame.draw.rect(screen, current_color, button_rect, border_radius=10)
    
    # Text
    text_surf = font.render(text, True, pygame.Color("white"))
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    
    return button_rect

def mode_menu():
    while True:
        screen.fill((30, 30, 30)) # Dark background to match your side panel
        
        title_surf = font.render("CHOOSE YOUR CHALLENGE", True, pygame.Color("lightgray"))
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 100))

        # Create Buttons
        pvp_btn = draw_button("Player vs Player", 200, (50, 100, 50), (70, 150, 70))
        pvc_btn = draw_button("Player vs Computer", 300, (100, 50, 50), (150, 70, 70))
        back_btn = draw_button("Back to Menu", 400, (80, 80, 80), (120, 120, 120))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_btn.collidepoint(event.pos):
                    return "PVP"
                if pvc_btn.collidepoint(event.pos):
                    return "PVC"
                if back_btn.collidepoint(event.pos):
                    return "BACK"

        pygame.display.flip()

if __name__ == "__main__":
    choice = mode_menu()
    print(f"User selected: {choice}")