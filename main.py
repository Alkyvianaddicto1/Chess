import pygame

# --- Configuration ---
BOARD_WIDTH, HEIGHT = 512, 512
PANEL_WIDTH = 200  # Space for Score and Forfeit button
WIDTH = BOARD_WIDTH + PANEL_WIDTH
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    # 1. Load the sprite sheet from your main directory
    try:
        sheet = pygame.image.load("./images/chess-sprite.png").convert_alpha()
        sheet.set_colorkey((0, 0, 0))
    except:
        # Fallback if the file is missing
        print("Error: 'chess-sprite.jpg' not found.")
        return

    # 2. Get dimensions of the sheet
    sheet_width, sheet_height = sheet.get_size()
    
    # 3. Calculate piece size (6 columns, 2 rows)
    piece_w = sheet_width // 6
    piece_h = sheet_height // 2

    # 4. Map names to the horizontal order in chess-sprite.jpg
    # The order in your image is: Rook, Bishop, Queen, King, Knight, Pawn
    piece_order = ['R', 'B', 'Q', 'K', 'N', 'p']
    
    for row in range(2):
        # Row 0 is Black, Row 1 is White in the sprite sheet
        color = 'b' if row == 0 else 'w'
        for col in range(6):
            piece_name = color + piece_order[col]
            rect = pygame.Rect(col * piece_w, row * piece_h, piece_w, piece_h)
            # Crop and scale to fit board dimensions
            IMAGES[piece_name] = pygame.transform.smoothscale(sheet.subsurface(rect), (SQ_SIZE, SQ_SIZE))


class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.score = 0 
        self.piece_values = {"p": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}
        self.is_forfeited = False
        self.whiteCaptured = [] # Pieces white lost
        self.blackCaptured = [] # Pieces black lost

    def makeMove(self, move):
        # Update Score and Captured Lists only if a piece is actually captured
        if move.pieceCaptured != "--":
            # Track the captured piece for the UI gallery
            if move.pieceCaptured[0] == 'w':
                self.whiteCaptured.append(move.pieceCaptured)
            else:
                self.blackCaptured.append(move.pieceCaptured)
                
            # Calculate and update the numerical score
            val = self.piece_values[move.pieceCaptured[1]]
            self.score += val if self.whiteToMove else -val

        # Execute the physical move on the board
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        
        # Swap turns
        self.whiteToMove = not self.whiteToMove
        
        # Update king's location if the King was the piece moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            # Reverse score on undo
            if move.pieceCaptured != "--":
                if move.pieceCaptured[0] == 'w':
                    self.whiteCaptured.pop()
                else:
                    self.blackCaptured.pop()

                val = self.piece_values[move.pieceCaptured[1]]
                self.score -= val if self.whiteToMove else -val

            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

    def getValidMoves(self):
        moves = self.getAllPossibleMoves()
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove 
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove 
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        return moves
    
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # Diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow, endCol = r + d[0] * i, c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: break # Ally piece
                else: break # Off board
    
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow, endCol = r + m[0], c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if self.board[endRow][endCol][0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getQueenMoves(self, r, c, moves):
        # A Queen is just a Rook + a Bishop
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: 
            if r-1 >= 0 and self.board[r-1][c] == "--": 
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": 
                    moves.append(Move((r, c), (r-2, c), self.board))
            if r-1 >= 0 and c-1 >= 0: 
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if r-1 >= 0 and c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else: 
            if r + 1 < 8:
                if self.board[r+1][c] == "--":
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r, c), (r+2, c), self.board))
                if c-1 >= 0:
                    if self.board[r+1][c-1][0] == 'w':
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                if c+1 <= 7:
                    if self.board[r+1][c+1][0] == 'w':
                        moves.append(Move((r, c), (r+1, c+1), self.board))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow, endCol = r + d[0] * i, c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: break
                else: break

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow, endCol = r + kingMoves[i][0], c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

class Move:
    def __init__(self, startSq, endSq, board):
        self.startRow, self.startCol = startSq
        self.endRow, self.endCol = endSq
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

def main():
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

    while running:
        forfeit_btn = drawSidePanel(screen, gs)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver: # Only allow moves if game is not over
                    location = pygame.mouse.get_pos()
                    
                    if forfeit_btn.collidepoint(location):
                        gameOver = True
                        gs.is_forfeited = Truemenu

                # Ensure click is on the board
                if location[0] <= BOARD_WIDTH:
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
                if e.key == pygame.K_z:
                    gs.undoMove()
                    moveMade = True
                    gameOver = False # Reset gameOver state on undo
                if e.key == pygame.K_r:
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected, playerClicks = (), []
                    moveMade = False
                    gameOver = False # Reset gameOver state on reset

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        pygame.display.flip()

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(pygame.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def getQueenMoves(self, r, c, moves):
        # A Queen is just a Rook + a Bishop
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

def drawSidePanel(screen, gs):
    font = pygame.font.SysFont("Arial", 22, True)
    
    # 1. Create a semi-transparent surface for the "blurred/glass" effect
    # Medium-dark gray (50, 50, 50) at 160 alpha allows both piece colors to be visible
    panel_surface = pygame.Surface((PANEL_WIDTH, HEIGHT))
    panel_surface.set_alpha(160) 
    panel_surface.fill((50, 50, 50)) 
    screen.blit(panel_surface, (BOARD_WIDTH, 0))

    # 2. Draw a separator line
    pygame.draw.line(screen, (200, 200, 200), (BOARD_WIDTH, 0), (BOARD_WIDTH, HEIGHT), 2)

    # --- Score & Turn ---
    score_text = f"Score: {gs.score}"
    color = pygame.Color("green") if gs.score >= 0 else pygame.Color("red")
    screen.blit(font.render(score_text, True, color), (BOARD_WIDTH + 20, 30))
    
    turn = "White's Turn" if gs.whiteToMove else "Black's Turn"
    screen.blit(font.render(turn, True, pygame.Color("white")), (BOARD_WIDTH + 20, 70))

    # --- Captured Pieces Gallery ---
    small_sq = 25 
    screen.blit(font.render("Captured:", True, pygame.Color("lightgray")), (BOARD_WIDTH + 20, 130))
    
    # Draw Black pieces captured (White captures them)
    for i, piece in enumerate(gs.blackCaptured):
        if IMAGES[piece]:
            img = pygame.transform.smoothscale(IMAGES[piece], (small_sq, small_sq))
            x = BOARD_WIDTH + 20 + (i % 6) * (small_sq + 4)
            y = 160 + (i // 6) * (small_sq + 4)
            screen.blit(img, (x, y))

    # Draw White pieces captured (Black captures them)
    for i, piece in enumerate(gs.whiteCaptured):
        if IMAGES[piece]:
            img = pygame.transform.smoothscale(IMAGES[piece], (small_sq, small_sq))
            x = BOARD_WIDTH + 20 + (i % 6) * (small_sq + 4)
            y = 280 + (i // 6) * (small_sq + 4)
            screen.blit(img, (x, y))

    # --- Forfeit Button ---
    btn_rect = pygame.Rect(BOARD_WIDTH + 25, 430, 150, 45)
    mouse = pygame.mouse.get_pos()
    btn_color = (200, 0, 0) if btn_rect.collidepoint(mouse) else (150, 0, 0)
    pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)
    
    btn_text = font.render("FORFEIT", True, pygame.Color("white"))
    screen.blit(btn_text, (btn_rect.x + 35, btn_rect.y + 10))
    
    return btn_rect

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                if IMAGES[piece]:
                    screen.blit(IMAGES[piece], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    font = pygame.font.SysFont("Arial", 16, True, False)
                    text = font.render(piece, 0, pygame.Color('Red'))
                    screen.blit(text, pygame.Rect(c*SQ_SIZE + 10, r*SQ_SIZE + 10, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()