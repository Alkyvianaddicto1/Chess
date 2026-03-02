import pygame

# Board Themes: (Light Square Color, Dark Square Color)
BOARD_THEMES = {
    "Classic": (pygame.Color("white"), pygame.Color("gray")),
    "Green": (pygame.Color("#eeeed2"), pygame.Color("#769656")),  # Lichess Default
    "Blue": (pygame.Color("#ebecd0"), pygame.Color("#779bb0")),
    "Dark": (pygame.Color("#777777"), pygame.Color("#333333")),
    "Wood": (pygame.Color("#d9ab89"), pygame.Color("#836141")),
    "Ocean": (pygame.Color("#dee3e6"), pygame.Color("#8ca2ad")),
    "Purple": (pygame.Color("#efefff"), pygame.Color("#8877b1")),
    "Sand": (pygame.Color("#f0d9b5"), pygame.Color("#b58863")),   # Classic Wood/Vinyl
    "Emerald": (pygame.Color("#adbd8f"), pygame.Color("#698a4d")),
    "Midnight": (pygame.Color("#6f7378"), pygame.Color("#2d2e30")),
    "Bubblegum": (pygame.Color("#fce4ec"), pygame.Color("#f06292")),
    "Marble": (pygame.Color("#e2e2e2"), pygame.Color("#949494")),
    "Icy Sea": (pygame.Color("#daeaf1"), pygame.Color("#3d5a80")),
    "Tournament": (pygame.Color("#ffffdd"), pygame.Color("#80a080"))
}

# UI Constants
LINE_HEIGHT = 22
PANEL_BG_COLOR = (30, 30, 30)