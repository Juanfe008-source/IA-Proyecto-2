import pygame, copy
from pieces import *
from setting import Config, sounds
from tools import Position, OnBoard
from utils import GetSprite
import math
from Fen import *

class Board:
    def __init__(self):
        # 0 -> blancas , 1 -> negras
        self.player = 0 # Empiezan blancas
        self.historic = []
        self.moveIndex = 1
        self.font = pygame.font.SysFont("Consolas", 18, bold=True)
        self.grid = FEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR") 
        #self.grid = FEN("R7/5k3/R7/8/8/8/8/3QK3")
        
        #Almacenará las instancias del rey blanco y negro respectivamente
        self.capturedPiece = None
        self.WhiteKing = None
        self.BlackKing = None
        #Busca las instancias de los reyes en la cuadricula por medio de su color y codigo y las asigna a su respectiva variable 
        for pieces in self.grid:
            for piece in pieces:
                if piece != None:
                    if piece.color == 0 and piece.code == "k":
                        self.WhiteKing = piece
                    elif piece.color == 1 and piece.code == "k":
                        self.BlackKing = piece

        # Indica si algún rey está en jaque
        self.checkWhiteKing = False
        self.checkBlackKing = False

        self.winner = None # Almacena al ganador del juego (si lo hay)
        self.pieceToPromote = None #Almacena la pieza a promover

        #Listas con las opciones de promoción disponibles
        self.whitePromotions = [Queen(Position(0, 0), 0), Bishop(Position(0, 1), 0), Knight(Position(0, 2), 0), Rook(Position(0, 3), 0)]
        self.blackPromotions = [Rook(Position(0, 7), 1), Knight(Position(0, 6), 1), Bishop(Position(0, 5), 1), Queen(Position(0, 4), 1)]

    def GetPiece(self, coord):
        return self.grid[coord.x][coord.y]

    def SetPiece(self, position, piece):
        self.grid[position.x][position.y] = piece

    def SwitchTurn(self):
        "Pasa de turno"
        # Cambia entre 0 y 1
        # (0 + 1) * -1 + 2 = 1
        # (1 + 1) * -1 + 2 = 0
        self.player = (self.player + 1 ) * -1 + 2
        # Revisa si el jugador ha perdido o no
        self.IsCheckmate()

    def RecentMove(self):
        return None if not self.historic else self.historic[-1]

    def RecentMovePositions(self):
        if not self.historic or len(self.historic) <= 1:
            return None, None
        pos = self.historic[-1][3]
        oldPos = self.historic[-1][4]

        return pos.GetCopy(), oldPos.GetCopy()

    def AllowedMoveList(self, piece, moves, isAI):
        "Genera las listas con los movimientos y capturas validados"
        allowed_moves = []
        for move in moves:
            if self.VerifyMove(piece, move.GetCopy(), isAI): # Si el movimiento es valido
                allowed_moves.append(move.GetCopy()) # Lo añade a la lista
        return allowed_moves

    def GetAllowedMoves(self, piece, isAI=False):
        "Obtiene los movimientos permitidos"
        moves, captures = piece.GetMoves(self) # Obtiene una tupla y guarda cada elemento en su respectiva variable
        allowed_moves = self.AllowedMoveList(piece, moves.copy(), isAI)  
        allowed_captures = self.AllowedMoveList(piece, captures.copy(), isAI)
        return allowed_moves, allowed_captures # Retorna los movimientos permitidos y las capturas permitidas
    
    def GetPositionsToPut(self):
        posiciones_vacias = []
        # Recorrer filas y columnas del tablero
        for fila in range(8):
            for columna in range(8):
             # Verificar si la posición está vacía 
                if self.grid[fila][columna] == None:
                    posiciones_vacias.append((fila, columna))

        return posiciones_vacias

    def Move(self, piece, position, captura=False, IAGame = False):
        "Tipo de movimiento a realizar"
   
        if position != None: # Si hay una posición valida
            position = position.GetCopy()
            if self.isCastling(piece, position.GetCopy()): # Si se puede hacer enroque
                self.CastleKing(piece, position.GetCopy()) # Hace el enroque
            elif self.isEnPassant(piece, position.GetCopy()): # Si se puede comer al paso
                self.grid[position.x][piece.position.y] = None
                self.MovePiece(piece, position)
                self.historic[-1][2] = piece.code + " EP"
            else:
                if IAGame:
                    # Turno de la IA
                    if self.player == 1:
                        if self.GetPiece(position) != None:
                            self.SaveCapturedPiece(position)
                            self.MovePiece(piece, position)
                        else:
                            self.MovePiece(piece, position)

                    # Turno del jugador
                    else:
                        if captura:
                            self.SaveCapturedPiece(position)
                            self.MovePiece(piece, position) # Va a mover la pieza
            
                        else: 
                            self.MovePiece(piece, position)   
                else:
                    if captura:
                        self.SaveCapturedPiece(position)
                        self.MovePiece(piece, position) # Va a mover la pieza
            
                    else:
                        self.MovePiece(piece, position)   

                # Revisa para promover
                if type(piece) == Pawn and (piece.position.y == 0 or piece.position.y == 7):
                    self.pieceToPromote = piece
                    
                self.Check()     
            
    def SaveCapturedPiece(self, position):
        "Guarda la pieza capturada"
        positionAux = position.GetCopy()
        self.capturedPiece = self.GetPiece(positionAux)
        newPosition = Position(3,3)
        self.capturedPiece.updatePosition(newPosition)
        self.grid[positionAux.x][positionAux.y] = None
        self.ChangeColor(self.capturedPiece)
    
    def ChangeColor(self, piece):
        "Cambio de bando para las piezas capturadas"
        if piece.color == 1:
            piece.color = 0
            piece.sprite = GetSprite(piece)

        else:
            piece.color = 1
            piece.sprite = GetSprite(piece)

    def PutCapturedPiece(self, position):
        "Posicionar las piezas capturadas"
        self.capturedPiece.updatePosition(position)
        self.grid[position.x][position.y] = self.capturedPiece
                           
    def MovePiece(self, piece, position):
        "Mover las piezas"
        position = position.GetCopy()
        self.grid[piece.position.x][piece.position.y] = None # Deja vacia la casilla original de la pieza
        old_position = piece.position.GetCopy() # Almacena la Posición de la casilla original de la pieza
        piece.updatePosition(position) # Pasa como parametro la posición ajustada del mouse (casilla nueva donde se colocará la pieza)
        self.grid[position.x][position.y] = piece # Asigna la pieza a la nueva casilla
        self.historic.append([self.moveIndex, piece.color, piece.code, old_position, piece.position, piece]) # Añade información al historial de movimientos
        piece.previousMove = self.moveIndex
        self.moveIndex += 1
        self.checkBlackKing = False
        self.checkWhiteKing = False

    def VerifyMove(self, piece, move, isAI):
        "verifica el movimiento revisando todos los resultados posibles"
        # Esta función retornará False si el oponente va a responder capturando al rey
        position = move.GetCopy()
        oldPosition = piece.position.GetCopy()
        captureEnPassant = None
        capturedPiece = self.grid[position.x][position.y]
        if self.isEnPassant(piece, position):
            captureEnPassant = self.grid[position.x][oldPosition.y]
            self.grid[position.x][oldPosition.y] = None

        self.grid[oldPosition.x][oldPosition.y] = None
        self.grid[position.x][position.y] = piece
        piece.updatePosition(move)
        EnemyCaptures = self.GetEnemyCaptures(self.player)
        if self.isCastling(piece, oldPosition):
            if math.fabs(position.x - oldPosition.x) == 2 and not self.VerifyMove(piece, Position(5, position.y), isAI) \
                or math.fabs(position.x - oldPosition.x) == 3 and not self.VerifyMove(piece, Position(3, position.y), isAI) \
                or self.IsInCheck(piece):
                self.UndoMove(piece, capturedPiece, oldPosition, position)
                return False

        for pos in EnemyCaptures:
            if (self.WhiteKing.position == pos and piece.color == 0) \
                or (self.BlackKing.position == pos and piece.color == 1):
                self.UndoMove(piece, capturedPiece, oldPosition, position)
                if captureEnPassant != None:
                    self.grid[position.x][oldPosition.y] = captureEnPassant
                return False
            
        self.UndoMove(piece, capturedPiece, oldPosition, position)
        if captureEnPassant != None:
            self.grid[position.x][oldPosition.y] = captureEnPassant
        return True

    def UndoMove(self, piece, captured, oldPos, pos):
        "Deshacer movimiento"
        self.grid[oldPos.x][oldPos.y] = piece
        self.grid[pos.x][pos.y] = captured
        piece.updatePosition(oldPos)

    def GetEnemyCaptures(self, player):
        "Obtener las capturas enemigas"
        captures = []
        for pieces in self.grid:
            for piece in pieces:
                if piece != None and piece.color != player:
                    moves, piececaptures = piece.GetMoves(self)
                    captures = captures + piececaptures
        return captures

    def isCastling(self, king, position):
        "Verifica si se puede hacer enroque"
        return type(king) == King and abs(king.position.x - position.x) > 1

    def isEnPassant(self, piece, newPos):
        "Verifica si se puede comer al paso"
        if type(piece) != Pawn: # Si la pieza no es un peón 
            return False
        moves = None
        if piece.color == 0:
            moves = piece.EnPassant(self, -1)
        else:
            moves = piece.EnPassant(self, 1)
        return newPos in moves

    def IsInCheck(self, piece):
        "Verifica si está en jaque"
        return type(piece) == King and \
                ((piece.color == 0 and self.checkWhiteKing) or (piece.color == 1 and self.checkBlackKing))

    def CastleKing(self, king, position):
        "Hacer enroque"
        position = position.GetCopy()
        if position.x == 2 or position.x == 6:
            if position.x == 2:
                rook = self.grid[0][king.position.y]
                self.MovePiece(king, position)
                self.grid[0][rook.position.y] = None
                rook.position.x = 3
            else:
                rook = self.grid[7][king.position.y]
                self.MovePiece(king, position)
                self.grid[7][rook.position.y] = None
                rook.position.x = 5

            rook.previousMove = self.moveIndex - 1
            self.grid[rook.position.x][rook.position.y] = rook
            self.historic[-1][2] = king.code + " C"
            sounds.castle_sound.play()

    def PromotePawn(self, pawn, choice):
        "Promover Peon"
        if choice == 0:
            self.grid[pawn.position.x][pawn.position.y] = Queen(pawn.position.GetCopy(), pawn.color)
        elif choice == 1:
            self.grid[pawn.position.x][pawn.position.y] = Bishop(pawn.position.GetCopy(), pawn.color)
        elif choice == 2:
            self.grid[pawn.position.x][pawn.position.y] = Knight(pawn.position.GetCopy(), pawn.color)
        elif choice == 3:
            self.grid[pawn.position.x][pawn.position.y] = Rook(pawn.position.GetCopy(), pawn.color)

        self.SwitchTurn()
        self.Check()
        self.pieceToPromote = None

    def MoveSimulation(self, piece, next_pos):
        "Simula movimienots para Evaluarlos movimientos"
        if self.grid[next_pos.x][next_pos.y] == None:
            self.grid[piece.position.x][piece.position.y] = None
            piece.position = next_pos.GetCopy()
            self.grid[next_pos.x][next_pos.y] = piece
            return None
        else:
            prev_piece = self.grid[next_pos.x][next_pos.y]
            self.grid[piece.position.x][piece.position.y] = None
            piece.position = next_pos.GetCopy()
            self.grid[next_pos.x][next_pos.y] = piece
            return prev_piece

    def Check(self):
        if self.player == 0:
            king = self.WhiteKing
        else:
            king = self.BlackKing

        for pieces in self.grid:
            for piece in pieces:
                if piece != None and piece.color != self.player:
                    moves, captures = self.GetAllowedMoves(piece)
                    if king.position in captures:
                        if self.player == 1:
                            self.checkBlackKing = True
                            return
                        else:
                            self.checkWhiteKing = True
                            return

    def IsCheckmate(self):
        "Jaque Mate"
        for pieces in self.grid:
            for piece in pieces:
                if piece != None and piece.color == self.player:
                    moves, captures = self.GetAllowedMoves(piece)
                    # Si hay algún movimiento legal faltante entonces no hay Jaque mate
                    if moves or captures:
                        return False
        self.Check()
        if self.checkWhiteKing:
            # Gana negro
            self.winner = 1
        elif self.checkBlackKing:
            # Gana blanco
            self.winner = 0
        else:
            # Empate
            self.winner = -1
        return True
