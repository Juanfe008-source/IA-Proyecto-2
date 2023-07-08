import pygame
from setting import Config, sounds
from screens.chess import Chess
import ui

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.vscomputer = ui.Button(screen, Config.width//2, Config.height//2, 200, 80, "Vs IA")
        self.multiplayer = ui.Button(screen, Config.width//2, Config.height//2 + 100, 200, 80, "Multijugador")
        self.exit = ui.Button(screen, Config.width//2, Config.height//2 + 200, 200, 80, "Salir")
        self.background = pygame.image.load("./assets/images/background2.jpg")
        self.background = pygame.transform.smoothscale(self.background, Config.resolution)
        self.title1 = ui.TextUI(self.screen, "AJEDREZ", Config.width//1.2, Config.height//6, 140, (255, 255, 255))
        self.title2 = ui.TextUI(self.screen, "LOCO", Config.width//1.2, Config.height//3.15, 140, (255, 255, 255))
        self.title1.centered = True
        self.title2.centered = True
        self.running = True
        self.chess = Chess(screen)

    #Dibuja los botones y textos junto con sus respectivas actualizaciones
    def DrawButtons(self): 
        self.vscomputer.Draw()
        self.multiplayer.Draw()
        self.exit.Draw()
        self.title1.Draw()
        self.title2.Draw()
    
    #Verifica si el click se dió en un boton y dependiendo del boton ejecuta una acción diferente
    def HandleClick(self):
        mouse_position = pygame.mouse.get_pos() #Obtiene la posición del mouse
        if self.vscomputer.get_rect().collidepoint(mouse_position): #Verifica si el mouse está encima del boton vscomputer
            self.chess.gameOver = False #Determina que el juego va a empezar o va a reanudarse
            self.chess.vsComputer() #Empieza el modo contra la maquina
        elif self.multiplayer.get_rect().collidepoint(mouse_position): #Verifica si el mouse está encima del boton multiplayer
            self.chess.gameOver = False #Determina que el juego va a empezar o va a reanudarse
            self.chess.multiplayer() #Empieza el modo multijugador
        elif self.exit.get_rect().collidepoint(mouse_position): #Verifica si el mouse está encima del boton exit
            self.running = False #Finaliza el bucle

    # Bucle principal
    def Run(self):
        while self.running: # Mientras running sea verdadero se ejecutará el bucle
            # Mostrar la imagen de fondo
            self.screen.blit(self.background, (0, 0))
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Si se cierra el programa
                    self.running = False # Finaliza el bucle
                elif event.type == pygame.KEYUP: # Si se presiona una tecla
                    if event.key == pygame.K_ESCAPE: # Si esa tecla es "ESCAPE"
                        self.running = False # Finaliza el bucle
                elif event.type == pygame.MOUSEBUTTONUP: # Si se da un click
                    if event.button == 1: # Si es un click izquierdo
                        self.HandleClick() # Ejecuta el manejo del click

            self.DrawButtons() # Ejecuta el dibujo de los botones
            # Actualiza la pantalla
            pygame.display.update()
