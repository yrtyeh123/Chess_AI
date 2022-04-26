class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible


    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players
        # update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

    '''
    Undo th last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back
            # update the king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
    '''
    All moves considering checks
    nums = [0,1,2,3,3,4,5]
    for num in nums:
        if num == 3:
            nums.remove(num)
    '''

    def getValidMoves(self):
        moves = self.getAllPossibleMoves()
        # 2 for each move, make the move
        for i in range(len(moves)-1, -1,-1): # when removing from a list go backwards through that list
            self.makeMove(moves[i])
            # 3 generate all opponent's moves
            oppMoves = self.getAllPossibleMoves()
            # 4 for each of your opponent's moves , see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: #either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves

    '''
    Determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if the enemy player can attack the square
    '''
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # Swicth turns back
        for move in oppMoves:
            if move.endRow == row and move.endCol == col: # square is under attack
                return True
        return False
    '''
    All moves without considering checks
    '''

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                turn = self.board[row][col][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row,col,moves) #calls the appropriate move function based on piece type
        return moves

    '''
    Get all the pawn moves for the pawn located at row,col and add these moves to the list
    '''

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove:  # white pawn moves
            if self.board[row - 1][col] == "--":  # square pawn advance
                moves.append(Move((row, col), (row - 1, col), self.board))
                # Tốt trắng nằm ở hàng số 6 trong mảng
                if row == 6 and self.board[row-2][col] == "--": #2 square pawn advance
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row-1][col-1][0] == 'b': # enemy piece to capture
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7:
                if self.board[row-1][col-1][0] == 'b': # enemy piece to capture
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
        else: # black pawn moves
            if self.board[row+1][col] == "--": # 1 square move
                moves.append(Move((row, col), (row + 1, col), self.board))
                # tốt đen nằm ở hàng số 1 trong mảng
                if row == 1 and self.board[row+2][col] == "--": #2 square pawn advance
                    moves.append(Move((row, col), (row + 2, col), self.board))
            # capture
            if col - 1 >= 0:
                if self.board[row+1][col-1][0] == 'w': # enemy piece to capture
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:
                if self.board[row+1][col-1][0] == 'w': # enemy piece to capture
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
        # ađ pawn promotion later
    '''
    Get all the rook moves for the pawn located at row,col and add these moves to the list
    '''
    def getRookMoves(self, row, col, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # (up,left,down,right)
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty square valid
                        moves.append(Move((row,col), (endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid
                        moves.append(Move((row,col), (endRow,endCol),self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break

    '''
    Get all the knight moves for the pawn located at row,col and add these moves to the list
    '''
    def getKnightMoves(self, row, col, moves):
        knightMoves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8  and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((row,col), (endRow, endCol), self.board))

    '''
    Get all the bishop moves for the pawn located at row,col and add these moves to the list
    '''
    def getBishopMoves(self, row, col, moves):
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))  # (up_left,down_left,up_right,down_right)
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8): # bishop can move max of 7 squares
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty square valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break

    '''
    Get all the queen moves for the pawn located at row,col and add these moves to the list
    '''
    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row,col,moves)
        self.getBishopMoves(row,col,moves)

    '''
    Get all the king moves for the pawn located at row,col and add these moves to the list
    '''
    def getKingMoves(self, row, col, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = row + kingMoves[i][0]
            endCol = col + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((row, col), (endRow, endCol), self.board))

class Move():
    # maps keys to values
    # key : value
    # Trên bàn cờ thì ô trên cùng bên trái là [a][8] nhưng trong mảng thì ô bắt đầu sẽ là [0][0]
    # nên ta chuyển đổi từ kí hiệu nhập trên bàn cờ chơi sang mảng để di chuyển quân cờ
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassantPossible = ()):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        #self.isPawnPromotion = False
        #if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            #self.isPawnPromotion = True
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # en passant
        #self.isEnpassantMove = False
        #if self.pieceMoved[1] == 'p' and (self.endRow,self.endCol) == enpassantPossible:
            #self.isEnpassantMove = True
        self.isEnpassantMove = (self.pieceMoved[1] == 'p' and (self.endRow,self.endCol) == enpassantPossible)


        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #print(self.moveID)

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowToRanks[row]
