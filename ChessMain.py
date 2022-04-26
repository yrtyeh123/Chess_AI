import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
Square_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ['wp', 'bp', 'wR', 'bR', 'wN', 'bN', 'wB', 'bB', 'wQ', 'bQ', 'wK', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("image/" + piece + ".png"), (Square_SIZE, Square_SIZE))


def main():
    p.init()
    # tai sao (WIDTH,HEIGHT) thi bi bug ma ((WIDTH,HEIGHT)) lai run
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("gray"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made

    # print(gs.board)
    loadImages()
    running = True
    squareSelected = ()  # no square is selected, keep track of the last click of the user (tupl: (row, col))
    playerClicks = []  # keep track of player clicks (two tuples: [(6,4), (4,4)]
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x,y) location of mouse
                col = location[0] // Square_SIZE
                row = location[1] // Square_SIZE
                if squareSelected == (row, col):  # the user clicked the same square twice
                    squareSelected = ()  # deselect
                    playerClicks = []  # clear player clicks
                else:
                    squareSelected = (row, col)
                    playerClicks.append(squareSelected)  # append for both 1st and 2nd clicks
                if len(playerClicks) == 2:  # after 2nd click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            squareSelected = ()  # reset user clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [squareSelected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * Square_SIZE, r * Square_SIZE, Square_SIZE, Square_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * Square_SIZE, r * Square_SIZE, Square_SIZE, Square_SIZE))


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)


if __name__ == '__main__':
    main()
