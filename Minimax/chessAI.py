from Minimax.PointMap import map_points, PieceMap
from pieces import Pawn
#import math

class Minimax(object):
    def __init__(self, depth, board, AlphBetaPruning=True, UsePointMaps=True):
        self.depth = depth
        self.board = board
        self.AlphaBetaPruning = AlphBetaPruning
        self.UsePointMaps = UsePointMaps

    def Start(self, depth):
        "Punto de entrada a MiniMax"
        bestMove = None
        bestScore = -9999
        currentPiece = None
        isMaximizer = False
        # Revisa si el jugador actual es el maximizador
        if self.board.player == 1:
            isMaximizer = True
        else:
            isMaximizer = False

        # Revisa si el jugador actual es el minimizador
        if isMaximizer == False:
            bestScore *= (-1) # Minimizador intenta minimizar la puntuación
        # Obtiene todos los posibles movimientos en el estado actual
        for pieces in self.board.grid:
            for piece in pieces:
                if piece != None and piece.color == self.board.player:
                    moves, captures = self.board.GetAllowedMoves(piece, True)
                    possibleMoves = captures + moves
                    for position in possibleMoves:
                        prev_pos = piece.position
                        pion = self.board.MoveSimulation(piece, position) # Inicializa la simulación de movimientos
                        score = self.minimax(depth + 1, not isMaximizer, -10000, 10000) # Evalua cada movimiento y obtiene su puntuación correspondiente
                        if type(piece) == Pawn and (position.y == 7 or position.y == 0): # Si el peon llega a la ultima fila
                            score += 80
                        elif self.board.isEnPassant(piece, position): # Si captura al paso
                            score += 10         
                        if not isMaximizer:
                            score *= (-1)
                        if score >= bestScore and isMaximizer: # Si la puntuación es mayor o igual que la mejor puntuación actual (solo aplica para el maximizador) 
                            bestScore = score # Actualiza puntuación
                            bestMove = position # Guarda el movimiento
                            currentPiece = piece # Guarda la pieza que lo va a realizar
                        # Se deshace el movimiento simulado para mantener el tablero en su estado original antes de pasar al siguiente movimiento.
                        if pion == None:
                            self.board.MoveSimulation(piece, prev_pos)
                        else:
                            self.board.MoveSimulation(piece, prev_pos)
                            self.board.MoveSimulation(pion, position)
        # Retorna la pieza actual y su mejor movimiento                    
        return currentPiece, bestMove

    def minimax(self, depth, isMaximizer, alpha, beta):
        "Función recursiva para hacer minimax"
        # Si se alcanza la profundidad maxima de busqueda se retorna la evaluación del estado actual del tablero 
        if self.depth == depth: # Condicion de parada
            return self.Evaluate() * (-1) # Se multiplicad por -1 para asegurar que retorne puntuaciones positivas para el maximizador y negativas para el minimizador

        if isMaximizer: # Si es el turno del maximizador
            bestScore = -9999 # (Alfa) Para asegurar que cualquier posición obtenida sea mayor que este valor 
            possibleMoves = self.LegalMoves(1, 7) # 7 porque es la ultima fila del tablero
            for _index in range(len(possibleMoves) -1, -1, -1): # Se exploran la lista de forma inversa para recorrer primero los movimientos más prometedores(que tienen más posibilidades de conducir a una mejor puntuación), al hacer esto se obtienen podas tempranas
                piece = possibleMoves[_index][1]
                i = possibleMoves[_index][2]
                prev_pos = piece.position # Guarda la posición anterior
                pion = self.board.MoveSimulation(piece, i) # Simulación de movimiento: actualiza temporalmente el tablero para reflejar el movimiento realizado.
                score = self.minimax(depth + 1, False, alpha, beta) # Llamado recursivo incrementando la profundidad, se cambia isMaximizer a False indicando que es el turno del minimizador
                bestScore = max(bestScore, score) # Se actualiza bestScore tomando el valor maximo entre el bestScore actual y el score obtenido
                if self.AlphaBetaPruning:
                    alpha = max(alpha, bestScore) # Se actualiza alpha tomando el valor maximo entre el alpha actual y bestScore
                self.UndoMove(pion, piece, prev_pos, i) # Se deshace el movimiento simulado, restaurando el tablero a su estado anterior

                if beta <= alpha and self.AlphaBetaPruning: # Condicion de corte, si se cumple se retorna bestScore sin explorar más nodos (Poda)
                    return bestScore
            return bestScore
        else: # Si es el turno del minimizador
            bestScore = 9999 #(Beta) Para asegurar que cualquier posición obtenida sea menor que este valor 
            possibleMoves = self.LegalMoves(0, 0) # 0 porque es la ultima fila del tablero
            for _index in range(len(possibleMoves) -1, -1, -1): # Se exploran la lista de forma inversa para recorrer primero los movimientos más prometedores(que tienen más posibilidades de conducir a una mejor puntuación), al hacer esto se obtienen podas tempranas
                piece = possibleMoves[_index][1]
                i = possibleMoves[_index][2]
                prev_pos = piece.position # Guarda la posición anterior
                currentPiece = self.board.MoveSimulation(piece, i) # Simulación de movimiento: actualiza temporalmente el tablero para reflejar el movimiento realizado.
                score = self.minimax(depth + 1, True, alpha, beta) # Llamado recursivo incrementando la profundidad, se cambia isMaximizer a True indicando que es el turno del minimizador
                bestScore = min(bestScore, score) # Se actualiza bestScore tomando el valor minimo entre el bestScore actual y el score obtenido
                if self.AlphaBetaPruning:
                    beta = min(beta, bestScore) # Se actualiza beta tomando el valor minimo entre el beta actual y bestScore
                self.UndoMove(currentPiece, piece, prev_pos, i) # Se deshace el movimiento simulado, restaurando el tablero a su estado anterior
                if beta <= alpha and self.AlphaBetaPruning: # Condicion de corte, si se cumple se retorna bestScore sin explorar más nodos (Poda)
                    return bestScore
            return bestScore

    def Evaluate(self):
        "Heuristica mapa de puntos"
        totalScore = 0
        for pieces in self.board.grid:
            for piece in pieces:
                if piece != None:
                    p_map = PieceMap(piece) 
                    score = piece.value # Valor de la pieza
                    if self.UsePointMaps:
                        score += p_map[piece.position.y][piece.position.x] # Se agrega al score el valor correspondiente en el mapa de puntos según la posición actual de la pieza
                    totalScore += score 

        return totalScore # Retorna la puntuación
    
    def UndoMove(self, currentPiece, piece, prev_pos, p):
        "Regresar el tablero a su estado anterior"
        if currentPiece == None:
            self.board.MoveSimulation(piece, prev_pos)
        elif currentPiece != None:
            self.board.MoveSimulation(piece, prev_pos)
            self.board.MoveSimulation(currentPiece, p)

    def GetMoves(self, piece, position):
        "Devuelve los movimientos posibles y los mejores movimientos para una pieza dada en una posición específica."
        possibleMoves = []
        bestMoves = []
        moves, captures = self.board.GetAllowedMoves(piece, True) # Obtiene todos los movimientos
        for pos in captures: # Se recorren las capturas 
            if self.board.grid[pos.x][pos.y] != None: # Si no está vacia
                # Se agrega un elemento a bestmoves 
                bestMoves.append([10 * self.board.grid[pos.x][pos.y].value - piece.value, piece, pos]) # Es el valor de la pieza capturada multiplicado por 10, menos el valor de la pieza actual, Pieza actual, Posicion de la captura
                if type(piece) == Pawn and (pos.y == position): # Si la pieza es un peon y la posición de la captura coincide con la posición objetivo
                    bestMoves[-1][0] == bestMoves[-1][0] + 90 # Se suman 90 puntos
            else: # Si está vacia
                bestMoves.append([piece.value, piece, pos]) # Valor de la pieza actual, pieza actual, posicion del movimiento
        for pos in moves:
            if type(piece) == Pawn and (pos.y == position):
                bestMoves.append([90, piece, pos])
            else:
                bestMoves.append([0, piece, pos])

        return possibleMoves, bestMoves

    def LegalMoves(self, color, pos):
        "Obtiene todos los movimientos legales"
        possibleMoves = []
        bestMoves = []
        for pieces in self.board.grid: # Recorre todas las piezas del tablero
            for piece in pieces:
                if piece != None and piece.color == color: # Si hay piezas y son del mismo color que el jugador actual
                    temp_moves, better_temp_moves = self.GetMoves(piece, pos)  
                    possibleMoves += temp_moves
                    bestMoves += better_temp_moves

        bestMoves.sort(key=lambda key: key[0]) # Ordena los elementos de menor a mayor según el valor del primer elemento de cada elemento (Puntuacion)
        possibleMoves = possibleMoves + bestMoves # se unen ambas listas
        return possibleMoves 
