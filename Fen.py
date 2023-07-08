from pieces import *
from utils import *
from setting import Config
from tools import Position

# Diccionario de piezas en notación FEN
def GetFenPieces(character, x, y):
    FenPieces = {
    # Blancas
    "K": King(Position(x, y), 0),
    "Q": Queen(Position(x, y), 0),
    "B": Bishop(Position(x, y), 0),
    "N": Knight(Position(x, y), 0),
    "R": Rook(Position(x, y), 0),
    "P": Pawn(Position(x, y), 0),

    # Negras
    "k": King(Position(x, y), 1),
    "q": Queen(Position(x, y), 1),
    "b": Bishop(Position(x, y), 1),
    "n": Knight(Position(x, y), 1),
    "r": Rook(Position(x, y), 1),
    "p": Pawn(Position(x, y), 1),
    }

    if character in FenPieces:
        return FenPieces[character]
    else:
        return None

# La función de la notación FEN retorna una cuadricula con las posiciones de las piezas
def FEN(positionstring):
    # inicializa la cuadricula vacia
    boardGrid = [[None for i in range(Config.boardSize)] for j in range(Config.boardSize)]
    # Posicionamiento de las piezas
    row = 0
    col = 0
    for character in positionstring:
        piece = GetFenPieces(character, row, col)
        # Si hay una pieza en la posición del string
        if piece:
            boardGrid[row][col] = piece # Asigna la pieza a esa casilla
            row +=1 # Se mueve a la derecha
        # Espacios vacios    
        elif character.isnumeric():
            row += int(character)
        #Salto de linea
        elif character == "/":
            col += 1
            row = 0
    
    return boardGrid


