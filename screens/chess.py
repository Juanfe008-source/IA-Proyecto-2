import pygame
import sys
import time
import random

from setting import Config, sounds
from tools import OnBoard, Position
from utils import ch
from board import Board
from Minimax.chessAI import Minimax
import ui

class Chess:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.gameOver = False
        self.board = Board()
        self.animateSpot = 1
        self.selectedPiece = None
        self.selectedPieceMoves = None
        self.selectedPieceCaptures = None
        self.positionsToPut = None
        self.captura = None 
        self.draggedPiece = None
        self.IAGame = None
        self.AdjustedMouse = Position(0, 0)
        self.gameOverBackground = pygame.image.load("./assets/images/gameover3.jpg")
        self.gameOverBackground = pygame.transform.smoothscale(self.gameOverBackground, Config.resolution)
        self.gameOverHeader = ui.TextUI(self.screen, "GAME OVER", Config.width//2, Config.height//6, 140, (255, 255, 255))
        self.gameOverHeader.centered = True
        self.winnerText = ui.TextUI(self.screen, " ", Config.width//2, Config.height//2 + 30, 110, (255, 255, 255))
        self.winnerText.centered = True

        # Minimax(profundidad, tablero, activar poda alfa-beta = Default(true), uso de mapas de puntos = Default(true))
        self.ComputerAI = Minimax(Config.AI_DEPTH, self.board, True, True)

    def vsComputer(self):
        pygame.event.clear()
        sounds.game_start_sound.play()
        while not self.gameOver:
            self.IAGame = True
            self.clock.tick(Config.fps)
            self.screen.fill((0, 0, 0))
            self.getMousePosition()
            # Actualiza el titulo de la ventana
            pygame.display.set_caption("Chess : VS Computer ")
            self.display()
            self.ComputerMoves(1)
            if self.gameOver == False:
                if self.animateSpot >= Config.spotSize:
                    self.HandleEvents()
                    self.IsGameOver()

    def multiplayer(self):
        pygame.event.clear() # Limpia la cola de eventos
        sounds.game_start_sound.play() # Activa el sonido de inicio de juego
        while not self.gameOver: # Se ejecuta mientras gameover sea falso
            self.IAGame = False
            self.clock.tick(Config.fps)
            self.screen.fill((0, 0, 0))
            self.getMousePosition()
            # Actualiza el titulo de la ventana
            pygame.display.set_caption("Chess : Multiplayer ")
            self.display()
            if self.animateSpot >= Config.spotSize: # Si se terminó la animación
                self.HandleEvents() #Manejo de eventos
            self.IsGameOver()

    def display(self):
        "Pantalla"
        self.Render()
        pygame.display.update()

    def HandleEvents(self):
        "Manejo de eventos"
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Si se cierra el programa
                self.gameOver = True # Juego terminado
                # cerrar Pygame
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP: # Se presiona una tecla
                if event.key == pygame.K_ESCAPE: #Si es escape
                    self.gameOver = True
                # Si es arriba o abajo cambian el tema del tablero
                if event.key == pygame.K_UP:
                    if Config.themeIndex < len(Config.themes) -1 :
                        Config.themeIndex += 1
                    else:
                        Config.themeIndex = 0
                if event.key == pygame.K_DOWN:
                    if Config.themeIndex > 0:
                        Config.themeIndex -= 1
                    else:
                        Config.themeIndex = len(Config.themes) -1
            elif event.type == pygame.MOUSEBUTTONDOWN: # Si se da un click
                if event.button == 1:
                    self.HandleOnLeftMouseButtonDown() # Presionar
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.HandleOnLeftMouseButtonUp() # Soltar

    def ComputerMoves(self, player):
        "Movimientos de la IA"
        if self.board.player == player:
            piece, bestmove = self.ComputerAI.Start(0)
            if bestmove:
                if self.board.GetPiece(bestmove) != None:
                    self.board.Move(piece, bestmove, captura = False, IAGame = True)
                    if self.board.pieceToPromote != None:
                        self.board.PromotePawn(self.board.pieceToPromote, 0)
                    self.positionsToPut = self.board.GetPositionsToPut()
                    nuevaPosicionCapturada = self.GeneratorOfIAPositions()
                    self.board.PutCapturedPiece(nuevaPosicionCapturada)
                    sounds.capture_sound.play()
                else:
                    self.board.Move(piece, bestmove, captura = False, IAGame = True)
                    if self.board.pieceToPromote != None:
                        self.board.PromotePawn(self.board.pieceToPromote, 0)
                    sounds.move_sound.play()
            self.positionsToPut = None
            self.board.SwitchTurn()

    def GeneratorOfIAPositions(self):
        randomTuple = random.choice(self.positionsToPut)
        x, y = randomTuple
        randomPosition = Position(x, y)
        return randomPosition
    
    def HandleOnLeftMouseButtonUp(self):
        "Manejo de soltar el click izquierdo"
        self.draggedPiece = None # Suelta la pieza
        if self.selectedPiece: # Si existe una pieza seleccionada
            if self.AdjustedMouse in self.selectedPieceCaptures: # Si la posición del mouse ajustada está en una posición de piezas a capturar
                self.board.Move(self.selectedPiece, self.AdjustedMouse, captura = True) # Mueve la pieza seleccionada para realizar la captura
                self.positionsToPut = self.board.GetPositionsToPut()
                sounds.capture_sound.play() # Activa el sonido de captura              
            elif self.AdjustedMouse in self.selectedPieceMoves : # Si la posición del mouse ajustada está en una posición disponible para mover
                self.board.Move(self.selectedPiece, self.AdjustedMouse, captura = False) # Mueve la pieza seleccionada a la casilla
                self.board.SwitchTurn()
                sounds.move_sound.play() # Activa el sonido de movimiento
                    
            self.ReleasePiece() # Libera la pieza

    def SelectPiece(self,piece):
        "Seleccionar pieza"
        if piece != None and piece.color == self.board.player: # Si hay una pieza y es del color del jugador actual
            self.selectedPiece = piece # Pieza seleccionada toma el valor de la pieza almacenada
            self.draggedPiece = piece # Pieza agarrada toma el valor de la pieza almacenada
            self.selectedPieceMoves, self.selectedPieceCaptures = self.board.GetAllowedMoves(self.selectedPiece) # Obtiene los movimientos posibles de la pieza agarrada junto con sus posibles capturas
            self.selectedOrigin = self.AdjustedMouse # Origen del seleccionado es la posición ajustada del mouse al momento de dar click

    def CheckEmptyPositions(self, position):
        nuevaPosicionCapturada = position.GetCopy()
        for posicion in self.positionsToPut:
            if nuevaPosicionCapturada.x == posicion[0] and nuevaPosicionCapturada.y == posicion[1]:
                # La nueva posición capturada es igual a una posición en la lista
                self.board.PutCapturedPiece(nuevaPosicionCapturada)
                self.positionsToPut = None
                self.board.SwitchTurn()
                break  # Termina el bucle si se encuentra una coincidencia
     
    def HandleOnLeftMouseButtonDown(self):
        "Manejo de presionar el click izquierdo"
        # Si hay una pieza a promover y la posición ajustada del mouse es la misma que la de la pieza 
        if self.board.pieceToPromote != None and self.AdjustedMouse.x == self.board.pieceToPromote.position.x: 
            choice = self.AdjustedMouse.y
            if choice <= 3 and self.board.player == 0:
                # promote pawn
                self.board.PromotePawn(self.board.pieceToPromote, choice)
                # refresh screen
                self.display()
            elif choice > 3 and self.board.player == 1:
                # promote pawn
                self.board.PromotePawn(self.board.pieceToPromote, 7-choice)
                # refresh screen
                self.display()
        
        elif self.positionsToPut:
            nuevaPosicionCapturada = self.AdjustedMouse 
            self.CheckEmptyPositions(nuevaPosicionCapturada) 

        # Si no hay piezas a promover ni capturas     
        else: 
            if OnBoard(self.AdjustedMouse): # Si el mouse se encuentra dentro del tablero de juego
                piece = self.board.grid[self.AdjustedMouse.x][self.AdjustedMouse.y] # Almacena la pieza de la posición ajustada en la que dio click el mouse
                self.SelectPiece(piece)

    def getMousePosition(self):
        "Obtener la posición ajustada del mouse"
        x, y = pygame.mouse.get_pos()
        x = (x - Config.horizontal_offset) // Config.spotSize
        y = (y - Config.top_offset//2) // Config.spotSize
        self.AdjustedMouse = Position(x, y)

    def IsGameOver(self):
        "Pregunta si el juego ha terminado"
        if self.board.winner != None: #Si hay un ganador
            self.gameOver = True # Termina el juego (rompe el bucle)
            self.display() 
            self.gameOverWindow()

    def ReleasePiece(self):
        "Soltar pieza (reinicia todos los valores de la misma)"
        self.selectedPiece = None
        self.selectedPieceMoves = None
        self.selectedPieceCaptures = None
        self.draggedPiece = None
        self.selectedOrigin = None

    def Render(self):
        "Dibujar tablero, piezas y resaltados"
        self.DrawChessBoard() #Tablero
        if self.animateSpot >= Config.spotSize: #Si la animación finalizó
            self.DrawPieces() #Dibuja las piezas
        self.DrawHighlight()
        if self.IAGame == True:
            if self.board.player == 0:
                self.DrawPositionsToPut()
                
        elif self.IAGame ==False:    
            self.DrawPositionsToPut()
     
    def DrawChessBoard(self):
        "Dibujar el tablero"
        if self.animateSpot < Config.spotSize:
            self.animateSpot += 2
        for i in range(Config.boardSize):
            for j in range(Config.boardSize):
                x = i * Config.spotSize + Config.horizontal_offset
                y = j * Config.spotSize + Config.top_offset // 2
                if (i + j) % 2 == 0:
                    pygame.draw.rect(self.screen, Config.themes[Config.themeIndex]["light"], [x, y, self.animateSpot, self.animateSpot])
                else:
                    pygame.draw.rect(self.screen, Config.themes[Config.themeIndex]["dark"], [x, y, self.animateSpot, self.animateSpot])

    def DrawChessCoordinate(self):
        "Dibujar coordenadas"
        for i in range(Config.boardSize):
            _x = 0.05 * Config.spotSize + Config.horizontal_offset
            _y = 0.05 * Config.spotSize + Config.top_offset + i * Config.spotSize
            color = Config.themes[Config.themeIndex]['dark'] if i % 2 == 0 else Config.themes[Config.themeIndex]['light']

            fontRenderer = Config.CoordFont.render(str(8-i), True, color)
            self.screen.blit(fontRenderer, (_x, _y))

            _x = 0.9 * Config.spotSize + Config.horizontal_offset + i * Config.spotSize
            _y = (Config.boardSize - 1) * Config.spotSize + Config.top_offset + Config.spotSize * 0.75
            color = Config.themes[Config.themeIndex]['light'] if i % 2 == 0 else Config.themes[Config.themeIndex]['dark']

            fontRenderer = Config.CoordFont.render(chr(ord("a")+ i), True, color)
            self.screen.blit(fontRenderer, (_x, _y))

    def DrawPieces(self):
        "Dibuja las piezas"
        # Dibuja posición vieja y nueva
        oldPosition, nPosition  = self.board.RecentMovePositions()
        if oldPosition and nPosition:
            x1 = oldPosition.x * Config.spotSize + Config.horizontal_offset
            y1 = oldPosition.y * Config.spotSize + Config.top_offset // 2
            x2 = nPosition.x * Config.spotSize + Config.horizontal_offset
            y2 = nPosition.y * Config.spotSize + Config.top_offset // 2
            pygame.draw.rect(self.screen, (0, 100, 100), [x1, y1, Config.spotSize, Config.spotSize])
            pygame.draw.rect(self.screen, (225, 120, 120), [x2, y2, Config.spotSize, Config.spotSize])    

        #Dibuja los sprites de las piezas    
        for x in range(Config.boardSize):
            for y in range(Config.boardSize):
                x_pos = x * Config.spotSize + Config.horizontal_offset
                y_pos = y * Config.spotSize + Config.top_offset // 2
                if self.board.grid[x][y] != None:
                    self.screen.blit(self.board.grid[x][y].sprite, (x_pos, y_pos))

    def DrawPositionsToPut(self):
        if self.positionsToPut != None:
            for position_x, position_y in self.positionsToPut:
                x = position_x * Config.spotSize + Config.horizontal_offset
                y = position_y * Config.spotSize + Config.top_offset // 2
                pygame.draw.rect(self.screen, (29, 161, 20), [x, y, Config.spotSize, Config.spotSize], Config.highlightOutline)

    def RenderPromoteWindow(self):
        "Ventana de promoción"
        if self.board.pieceToPromote:
            if self.board.pieceToPromote.color == 0:
                x = self.board.pieceToPromote.position.x * Config.spotSize + Config.horizontal_offset
                y = self.board.pieceToPromote.position.y * Config.spotSize + Config.top_offset // 2
                pygame.draw.rect(self.screen, (200, 200, 200), [x, y, Config.spotSize , Config.spotSize * 4])
                for i in range(4):
                    piece = self.board.whitePromotions[i]
                    self.screen.blit(piece.sprite, (x, i * Config.spotSize + Config.top_offset //2 ))
                    bottomY = i * Config.spotSize - 1
                    pygame.draw.rect(self.screen, (0, 0, 0), [x, bottomY, Config.spotSize , 2])
            else:
                x = self.board.pieceToPromote.position.x * Config.spotSize + Config.horizontal_offset
                y = (self.board.pieceToPromote.position.y - 3) * Config.spotSize + Config.top_offset // 2
                pygame.draw.rect(self.screen, (200, 200, 200), [x, y, Config.spotSize , Config.spotSize * 4])
                for i in range(4):
                    piece = self.board.blackPromotions[i]
                    self.screen.blit(piece.sprite, (x, (i+4) * Config.spotSize + Config.top_offset //2 ))
                    bottomY = (i + 4) * Config.spotSize - 1
                    pygame.draw.rect(self.screen, (0, 0, 0), [x, bottomY, Config.spotSize , 2])

    def DrawHighlight(self):
        "Dibujar resaltados"
        # Resaltado pieza seleccionada
        if self.selectedPiece != None:
            x = self.selectedPiece.position.x * Config.spotSize + Config.horizontal_offset
            y = self.selectedPiece.position.y * Config.spotSize + Config.top_offset // 2
            pygame.draw.rect(self.screen, (190, 200, 222), [x, y, Config.spotSize, Config.spotSize])
            if self.draggedPiece == None:
                self.screen.blit(self.selectedPiece.sprite, (x, y))

        # Dibujar los movimientos posibles de la pieza seleccionada
        if self.selectedPiece and self.selectedPieceMoves:
            for move in self.selectedPieceMoves:
                x = move.x * Config.spotSize + Config.horizontal_offset
                y = move.y * Config.spotSize + Config.top_offset // 2
                pygame.draw.rect(self.screen, (15, 140, 131), [x, y, Config.spotSize, Config.spotSize], Config.highlightOutline)

        # Dibujar las posibles capturas de la pieza seleccionada
        if self.selectedPiece and self.selectedPieceCaptures:
            for capturing in self.selectedPieceCaptures:
                x = capturing.x * Config.spotSize + Config.horizontal_offset
                y = capturing.y * Config.spotSize + Config.top_offset // 2
                self.screen.blit(ch, (x, y))

                # pygame.draw.rect(self.screen, (210, 211, 190), [x, y, Config.spotSize, Config.spotSize], Config.highlightOutline)
        # Dibujar la pieza levantada
        if self.draggedPiece != None:
            x = self.AdjustedMouse.x * Config.spotSize + Config.horizontal_offset
            y = self.AdjustedMouse.y * Config.spotSize + Config.top_offset // 2
            self.screen.blit(self.draggedPiece.sprite, (x, y))

        # Resalta si está en jaque
        # Rey blanco en jaque
        if self.board.checkWhiteKing:
            x = self.board.WhiteKing.position.x * Config.spotSize + Config.horizontal_offset
            y = self.board.WhiteKing.position.y * Config.spotSize + Config.top_offset // 2
            pygame.draw.rect(self.screen, (240, 111, 150), [x, y, Config.spotSize, Config.spotSize])
            self.screen.blit(self.board.WhiteKing.sprite, (x, y))
        # Rey negro en jaque
        elif self.board.checkBlackKing:
            x = self.board.BlackKing.position.x * Config.spotSize + Config.horizontal_offset
            y = self.board.BlackKing.position.y * Config.spotSize + Config.top_offset // 2
            pygame.draw.rect(self.screen, (240, 111, 150), [x, y, Config.spotSize, Config.spotSize])
            self.screen.blit(self.board.BlackKing.sprite, (x, y))

        if self.animateSpot >= Config.spotSize:
            self.DrawChessCoordinate()

        self.RenderPromoteWindow()

    def gameOverWindow(self):
        "Pantalla de juego terminada"
        if self.board.winner >= 0: # Si alguno de los jugadores ganó
            sounds.game_over_sound.play() # Activa el sonido de juego terminado
        else: # Si empataron
            sounds.stalemate_sound.play() # Activa el sonido de tablas
        time.sleep(2) # Duerme el programa durante 2 segundos
        self.screen.blit(self.gameOverBackground, (0, 0)) # Muestra la imagen de Game Over
        self.gameOverHeader.Draw() # Dibuja el texto de Game Over
        if self.board.winner  == 0:
            self.winnerText.text = "GANA EL BLANCO"
            self.winnerText.color = (255, 255, 255)
            self.screen.blit(self.board.WhiteKing.sprite, (Config.width//2 - Config.spotSize // 2, Config.height//3))
        elif self.board.winner == 1:
            self.winnerText.text = "GANA EL NEGRO"
            self.winnerText.color = (0, 0, 0)
            self.screen.blit(self.board.BlackKing.sprite, (Config.width//2 - Config.spotSize // 2, Config.height//3))
        else:
            self.winnerText.text = "EMPATE"
            self.winnerText.color = (179, 196, 195)

        self.gameOverHeader.Draw()
        self.winnerText.Draw()
        pygame.display.update()
        time.sleep(5)
        self.board = Board()
        self.animateSpot = 1
