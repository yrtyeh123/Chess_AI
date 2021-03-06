import pygame as p

import ChessEngine
import SmartMoveFinder
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512 # kích thước của bàn cờ 8 x 8
MOVE_LOG_PANEL_WIDTH = 250 # chiều rộng của phần hiển thị nước cờ
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT # chiều dài của phần hiển thị nước cờ
DIMENSION = 8 # kích thước bàn cờ gồm 8 ô
Square_SIZE = BOARD_HEIGHT // DIMENSION # kích thước của mỗi ô vuông tiêu chuẩn
MAX_FPS = 15  # for animations
IMAGES = {}

'''
Tải lên hình ảnh ban đầu của bàn cờ 
'''

def loadImages():
    pieces = ['wp', 'bp', 'wR', 'bR', 'wN', 'bN', 'wB', 'bB', 'wQ', 'bQ', 'wK', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("image/" + piece + ".png"), (Square_SIZE, Square_SIZE))


def main():
    global returnQueue
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    p.display.set_caption("Game cờ vua của nhóm 7")
    clock = p.time.Clock()
    #screen.fill(p.Color("pink"))
    moveLogFont = p.font.SysFont("Times New Roman", 12, False, False) # thông số của các nước đi
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    animate = False  # flag variable for when we should animate a move
    loadImages()
    running = True
    squareSelected = ()  # no square is selected, keep track of the last click of the user (tupl: (row, col))
    playerClicks = []  # keep track of player clicks (two tuples: [(6,4), (4,4)]
    gameOver = False
    playerOne = False # if a Human is playing white, then this will be True. If an AI is playing
    playerTwo = True  # Same as above for black
    AIThingking = False
    moveFinderProcess = None
    moveUndone = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // Square_SIZE
                    row = location[1] // Square_SIZE
                    # the user clicked the same square twice or user clicked move log
                    if squareSelected == (row, col) or col >= 8:
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
                                animate = True
                                squareSelected = ()  # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Bấm Z để đi lại nước đi của mình, nếu đấu vs AI thì bấm z 2 lần
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThingking:
                        moveFinderProcess.terminate()
                        AIThingking = False
                    moveUndone = True
                if e.key == p.K_r:  # Sau khi kết thúc, ta có thể bấm "r" để bắt đầu một game đấu mới
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThingking:
                        moveFinderProcess.terminate()
                        AIThingking = False
                    moveUndone = True

        # AI move finder:
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThingking:
                AIThingking = True
                print("thinking....")
                returnQueue = Queue()  # used to pass data between threads
                moveFinderProcess = Process(target=SmartMoveFinder.findBestMoves, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()  # call findBestMoves(gs, validMoves, returnQueue)

            if not moveFinderProcess.is_alive():
                print("don't thinking......")
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThingking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            drawEndGameText(screen, 'Stalemate' if gs.staleMate else 'Black win' if gs.whiteToMove else "White win")
            drawStartGameText(screen, " Bấm r để bắt đầu game mới")

            '''
            if gs.staleMate:
                text = 'Stalemate'
            else:
                if gs.whiteToMove:
                    text = 'Black win'
                else:
                    text = 'White win'
            drawEndGameText(screen, text + "\n" + "bấm r để bắt đầu game mới")            
            '''


        clock.tick(MAX_FPS)
        p.display.flip() # cập nhật nội dung của toàn bộ màn hình ( bao gồm cả phần chơi và phần hiển thị nước cờ).


'''
Responsible for all the graphics within a current game state
'''


def drawGameState(screen, gs, validMoves, squareSelected, moveLogFont):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)


'''
Draw the squares on the board. The top left square is always light.
'''


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * Square_SIZE, row * Square_SIZE, Square_SIZE, Square_SIZE))


'''
Highlight square selected and moves for piece selected
'''


def highlightSquares(screen, gs, validMoves, squareSelected):
    if squareSelected != ():
        row, col = squareSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((Square_SIZE, Square_SIZE))
            s.set_alpha(100)  # transperancy value -> 0 transparent; 255 opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (col * Square_SIZE, row * Square_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol * Square_SIZE, move.endRow * Square_SIZE))


'''
Draw the pieces on the board using the current GameState.board
'''


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col * Square_SIZE, row * Square_SIZE, Square_SIZE, Square_SIZE))


'''
Draw the move log
'''


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("pink"), moveLogRect) # hiển thị phông nền của phần ghi lại nước cờ
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + "w_" + moveLog[i].getChessNotation() + " "
        if i + 1 < len(moveLog):  # make sure black mad a move
            allyColor = "w_" if i % 2 == 1 else "b_"
            moveString += allyColor + moveLog[i + 1].getChessNotation()
        moveTexts.append(moveString)
    # 1. f2f5 f5f2
    # 2. e2e4 e7e5

    movesPerRow = 1
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = " "
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j] + " "

        textObject = font.render(text, True, p.Color('black'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


'''
Animation of moves
'''


def animateMove(move, screen, board, clock):
    global colors
    dRow = move.endRow - move.startRow # Hiệu tung độ
    dCol = move.endCol - move.startCol # Hiệu hoành độ
    framesPerSquare = 10  # số khung hình được hiển thị trên 1 đơn vị thời gian
    frameCount = (abs(dRow) + abs(dCol)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, col = (move.startRow + dRow * frame / frameCount, move.startCol + dCol * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * Square_SIZE, move.endRow * Square_SIZE, Square_SIZE, Square_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.enPassant:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * Square_SIZE, enPassantRow * Square_SIZE, Square_SIZE, Square_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        if move.pieceMoved != '--':
            screen.blit(IMAGES[move.pieceMoved], p.Rect(col * Square_SIZE, row * Square_SIZE, Square_SIZE, Square_SIZE))
        p.display.flip() # cập nhật toàn bộ màn hình
        clock.tick(60) #

'''
Sau khi game đấu kết thúc ( Đen thắng || Trắng thắng || Hoà ) in ra thông điệp của text
'''
def drawEndGameText(screen, text):
    font = p.font.SysFont("Times New Roman", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))
'''
Sau khi game đấu kết thúc, in ra chỉ dẫn để bắt đầu một game đấu khác
'''
def drawStartGameText(screen, text):
    font = p.font.SysFont("Times New Roman", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 + textObject.get_height() * 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == '__main__':
    main()
