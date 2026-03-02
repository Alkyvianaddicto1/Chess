import pygame
import random
import sys

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
        # Adjusted path to match standard local directory structures
        sheet = pygame.image.load("./images/chess-sprite.png").convert_alpha()
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

# --- Game Logic Classes ---

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
        self.whiteKingLocation, self.blackKingLocation = (7, 4), (0, 4)
        self.checkMate = self.staleMate = self.is_forfeited = False
        self.score = 0 
        self.piece_values = {"p": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}
        self.whiteCaptured, self.blackCaptured = [], []

    def makeMove(self, move):
        if move.pieceCaptured != "--":
            if move.pieceCaptured[0] == 'w': self.whiteCaptured.append(move.pieceCaptured)
            else: self.blackCaptured.append(move.pieceCaptured)
            val = self.piece_values[move.pieceCaptured[1]]
            self.score += val if self.whiteToMove else -val

        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK": self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK": self.blackKingLocation = (move.endRow, move.endCol)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            if move.pieceCaptured != "--":
                if move.pieceCaptured[0] == 'w': self.whiteCaptured.pop()
                else: self.blackCaptured.pop()
                val = self.piece_values[move.pieceCaptured[1]]
                self.score -= val if self.whiteToMove else -val
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK": self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK": self.blackKingLocation = (move.startRow, move.startCol)

    def getValidMoves(self):
        moves = self.getAllPossibleMoves()
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck(): moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck(): self.checkMate = True
            else: self.staleMate = True
        return moves

    def inCheck(self):
        return self.squareUnderAttack(*(self.whiteKingLocation if self.whiteToMove else self.blackKingLocation))

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove 
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove 
        return any(m.endRow == r and m.endCol == c for m in oppMoves)

    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'p': self.getPawnMoves(r, c, moves)
                    elif piece == 'R': self.getRookMoves(r, c, moves)
                    elif piece == 'N': self.getKnightMoves(r, c, moves)
                    elif piece == 'B': self.getBishopMoves(r, c, moves)
                    elif piece == 'Q': self.getQueenMoves(r, c, moves)
                    elif piece == 'K': self.getKingMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if r-1 >= 0 and self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": moves.append(Move((r, c), (r-2, c), self.board))
            for dc in [-1, 1]:
                if 0 <= r-1 < 8 and 0 <= c+dc < 8 and self.board[r-1][c+dc][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+dc), self.board))
        else:
            if r+1 < 8 and self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": moves.append(Move((r, c), (r+2, c), self.board))
            for dc in [-1, 1]:
                if 0 <= r+1 < 8 and 0 <= c+dc < 8 and self.board[r+1][c+dc][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+dc), self.board))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                er, ec = r + d[0]*i, c + d[1]*i
                if 0 <= er < 8 and 0 <= ec < 8:
                    if self.board[er][ec] == "--": moves.append(Move((r, c), (er, ec), self.board))
                    elif self.board[er][ec][0] == enemy:
                        moves.append(Move((r, c), (er, ec), self.board))
                        break
                    else: break
                else: break

    def getKnightMoves(self, r, c, moves):
        kMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally = "w" if self.whiteToMove else "b"
        for m in kMoves:
            er, ec = r + m[0], c + m[1]
            if 0 <= er < 8 and 0 <= ec < 8 and self.board[er][ec][0] != ally:
                moves.append(Move((r, c), (er, ec), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                er, ec = r + d[0]*i, c + d[1]*i
                if 0 <= er < 8 and 0 <= ec < 8:
                    if self.board[er][ec] == "--": moves.append(Move((r, c), (er, ec), self.board))
                    elif self.board[er][ec][0] == enemy:
                        moves.append(Move((r, c), (er, ec), self.board))
                        break
                    else: break
                else: break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally = "w" if self.whiteToMove else "b"
        for m in kMoves:
            er, ec = r + m[0], c + m[1]
            if 0 <= er < 8 and 0 <= ec < 8 and self.board[er][ec][0] != ally:
                moves.append(Move((r, c), (er, ec), self.board))

    def findGreedyMove(gs, validMoves):
        """Medium Difficulty: Picks the move with the highest value capture."""
        turnMultiplier = 1 if gs.whiteToMove else -1
        maxScore = -float('inf')
        bestMove = None
        
        for move in validMoves:
            gs.makeMove(move)
            if gs.checkMate:
                score = 999
            elif gs.staleMate:
                score = 0
            else:
                score = turnMultiplier * gs.score
            
            if score > maxScore:
                maxScore = score
                bestMove = move
            gs.undoMove()
        return bestMove if bestMove else random.choice(validMoves)


    def findBestMove(gs, validMoves, depth):
        """Hard/God Mode: Uses Minimax with Alpha-Beta Pruning."""
        global nextMove
        nextMove = None
        random.shuffle(validMoves)
        minimax(gs, depth, -10000, 10000, gs.whiteToMove)
        return nextMove if nextMove else random.choice(validMoves)

    def minimax(gs, depth, alpha, beta, isMaximizing):
        global nextMove
        if depth == 0 or gs.checkMate or gs.staleMate:
            return gs.score if isMaximizing else -gs.score

        validMoves = gs.getValidMoves()
        if isMaximizing:
            maxEval = -10000
            for move in validMoves:
                gs.makeMove(move)
                eval = minimax(gs, depth - 1, alpha, beta, False)
                gs.undoMove()
                if eval > maxEval:
                    maxEval = eval
                    if depth == 2 or depth == 3: # Adjust based on God Mode depth
                        nextMove = move
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return maxEval
        else:
            minEval = 10000
            for move in validMoves:
                gs.makeMove(move)
                eval = minimax(gs, depth - 1, alpha, beta, True)
                gs.undoMove()
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break
            return minEval

# --- UI and Main Logic ---

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
    
    # Mode Setup: playerOne is White (Human), playerTwo is Black (Human or AI)
    playerOne = True 
    playerTwo = True if mode == "PVP" else False 

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        forfeit_btn = drawSidePanel(screen, gs)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                running = False

            elif e.type == pygame.MOUSEBUTTONDOWN and not gameOver:
                location = pygame.mouse.get_pos()

                if forfeit_btn.collidepoint(location):
                    gs.is_forfeited = True
                    gameOver = True

                if gameOver:
                    return
                
                # HUMAN CLICK LOGIC
                if not gameOver and humanTurn and location[0] <= BOARD_WIDTH:
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
                        if not moveMade: playerClicks = [sqSelected]

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    gs.undoMove()
                    moveMade = True
                    gameOver = False
                if e.key == pygame.K_r:
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected, playerClicks = (), []
                    moveMade = False
                    gameOver = False

        # COMPUTER MOVE LOGIC (AI)
        if not gameOver and not humanTurn:
            if validMoves:
                pygame.time.delay(500) # Slight delay so moves aren't instant
                ai_move = random.choice(validMoves)
                gs.makeMove(ai_move)
                moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            drawEndGameText(screen, "Black wins by Checkmate" if gs.whiteToMove else "White wins by Checkmate")
        elif gs.staleMate:
            gameOver = True
            drawEndGameText(screen, "Stalemate")
        elif gs.is_forfeited:
            gameOver = True
            drawEndGameText(screen, "Game Over by Forfeit")

        clock.tick(MAX_FPS)
        pygame.display.flip()

# --- Drawing Functions ---

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            pygame.draw.rect(screen, colors[((r + c) % 2)], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

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

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                if IMAGES.get(piece):
                    screen.blit(IMAGES[piece], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawSidePanel(screen, gs):
    font = pygame.font.SysFont("Arial", 22, True)
    panel_surface = pygame.Surface((PANEL_WIDTH, HEIGHT))
    panel_surface.set_alpha(160) 
    panel_surface.fill((50, 50, 50)) 
    screen.blit(panel_surface, (BOARD_WIDTH, 0))
    pygame.draw.line(screen, (200, 200, 200), (BOARD_WIDTH, 0), (BOARD_WIDTH, HEIGHT), 2)
    
    score_text = f"Score: {gs.score}"
    screen.blit(font.render(score_text, True, (0,255,0) if gs.score >= 0 else (255,0,0)), (BOARD_WIDTH + 20, 30))
    turn_text = "White's Turn" if gs.whiteToMove else "Black's Turn"
    screen.blit(font.render(turn_text, True, (255,255,255)), (BOARD_WIDTH + 20, 70))

    small_sq = 25 
    for i, piece in enumerate(gs.blackCaptured):
        if IMAGES.get(piece):
            img = pygame.transform.smoothscale(IMAGES[piece], (small_sq, small_sq))
            screen.blit(img, (BOARD_WIDTH + 20 + (i % 6) * 30, 160 + (i // 6) * 30))
    for i, piece in enumerate(gs.whiteCaptured):
        if IMAGES.get(piece):
            img = pygame.transform.smoothscale(IMAGES[piece], (small_sq, small_sq))
            screen.blit(img, (BOARD_WIDTH + 20 + (i % 6) * 30, 280 + (i // 6) * 30))

    btn_rect = pygame.Rect(BOARD_WIDTH + 25, 430, 150, 45)
    mouse = pygame.mouse.get_pos()
    pygame.draw.rect(screen, (200,0,0) if btn_rect.collidepoint(mouse) else (150,0,0), btn_rect, border_radius=8)
    screen.blit(font.render("FORFEIT", True, (255,255,255)), (btn_rect.x + 35, btn_rect.y + 10))
    return btn_rect

def drawEndGameText(screen, text):
    font = pygame.font.SysFont("Arial", 32, True, False)
    text_surf = font.render(text, True, (255,255,255))
    bg_rect = pygame.Rect(0, 0, text_surf.get_width() + 20, text_surf.get_height() + 20)
    bg_rect.center = (BOARD_WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (0,0,0), bg_rect, border_radius=10)
    screen.blit(text_surf, (bg_rect.x + 10, bg_rect.y + 10))

if __name__ == "__main__":
    main()