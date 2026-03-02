import pygame
import random # Needed for AI

# --- Configuration ---
BOARD_WIDTH, HEIGHT = 512, 512
PANEL_WIDTH = 200 
WIDTH = BOARD_WIDTH + PANEL_WIDTH
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    try:
        # Standardize path and use convert_alpha for performance
        sheet = pygame.image.load("./images/chess-sprite.jpg").convert_alpha()
    except:
        print("Error: 'chess-sprite.jpg' not found.")
        return

    sheet_width, sheet_height = sheet.get_size()
    piece_w, piece_h = sheet_width // 6, sheet_height // 2
    piece_order = ['R', 'B', 'Q', 'K', 'N', 'p']
    
    for row in range(2):
        color = 'b' if row == 0 else 'w'
        for col in range(6):
            piece_name = color + piece_order[col]
            rect = pygame.Rect(col * piece_w, row * piece_h, piece_w, piece_h)
            IMAGES[piece_name] = pygame.transform.smoothscale(sheet.subsurface(rect), (SQ_SIZE, SQ_SIZE))

# ... [GameState and Move classes from your current code remain exactly the same] ...

def main(mode="PVP"):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Chess")
    clock = pygame.time.Clock()
    gs = GameState()
    loadImages()
    running, sqSelected, playerClicks = True, (), []
    validMoves = gs.getValidMoves()
    moveMade = False
    gameOver = False
    
    # Define players: True = Human, False = AI
    playerOne = True  # White is always human
    playerTwo = True if mode == "PVP" else False 

    while running:
        # Determine if it is currently a human's turn to move
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            
            # --- Human Input ---
            elif e.type == pygame.MOUSEBUTTONDOWN and not gameOver:
                location = pygame.mouse.get_pos() # Fixed: location defined here
                forfeit_btn = drawSidePanel(screen, gs)
                
                if forfeit_btn.collidepoint(location):
                    gs.is_forfeited = True
                    gameOver = True

                if humanTurn and location[0] <= BOARD_WIDTH:
                    col, row = location[0] // SQ_SIZE, location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected, playerClicks = (), []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    
                    if len(playerClicks) == 2:
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected, playerClicks = (), []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z: # Undo
                    gs.undoMove()
                    moveMade = True
                    gameOver = False
                if e.key == pygame.K_r: # Reset
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected, playerClicks = (), []
                    moveMade = False
                    gameOver = False

        # --- AI Move Logic ---
        if not gameOver and not humanTurn:
            if validMoves:
                # Basic AI: Picks a random valid move
                ai_move = random.choice(validMoves)
                gs.makeMove(ai_move)
                moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)
        
        # Check game states
        if gs.checkMate:
            gameOver = True
            drawEndGameText(screen, "Checkmate! " + ("Black wins" if gs.whiteToMove else "White wins"))
        elif gs.staleMate:
            gameOver = True
            drawEndGameText(screen, "Stalemate")
        elif gs.is_forfeited:
            drawEndGameText(screen, "Game Over by Forfeit")

        pygame.display.flip()
        clock.tick(MAX_FPS)