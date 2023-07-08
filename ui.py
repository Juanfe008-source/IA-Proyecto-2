import pygame
from setting import sounds

class TextUI:
    def __init__(self, screen, text, x, y, fontSize, color):
        self.screen = screen
        self.text = text
        self.x = x
        self.y = y
        self.fontSize = fontSize # Tamaño de la fuente
        self.color = color
        self.textColor = color
        self.font = pygame.font.Font("./assets/fonts/Champagne&Limousines.ttf", self.fontSize) # Se carga la fuente y se le asigna el tamaño
        self.centered = False
    
    #Dibuja el texto
    def Draw(self):
        mytext = self.font.render(self.text, True, self.textColor)

        if self.centered:
            text_rect = mytext.get_rect(center=(self.x , self.y))
            self.screen.blit(mytext, text_rect)
        else:
            self.screen.blit(mytext, (self.x, self.y))

class Button:
    def __init__(self, screen, x, y, w, h, text):
        self.screen = screen
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.thickness = 4 # Grosor del borde
        self.backgroundColor = (174, 7, 7) # Color default del boton
        self.outlineColor = (0, 0, 0) # Color del borde
        self.textColor = (255 ,255, 255) # Color del texto
        self.hoverColor = (98, 4, 4) # Color para cuando el mouse pase por encima
        self.fontSize = 24 # Tamaño de fuente
        self.font = pygame.font.Font("./assets/fonts/Champagne&Limousines.ttf", self.fontSize) # Se carga la fuente y se le asigna el tamaño
        self.tempcolor = self.backgroundColor # Color temporal se inicializa con backgroundcolor
        self.counter = 0 # Contador para controlar el sonido

    # Revisa si el mouse está por encima del boton para cambiar su color y activar el respectivo sonido
    def Hover(self):
        mouse_position = pygame.mouse.get_pos() # Obtiene la posición del mouse
        # Return 0 (el mouse no está encima) o 1 (el mouse está encima)
        if self.get_rect().collidepoint(mouse_position):
            self.tempcolor = self.hoverColor # Cambia el color default por hovercolor
            self.counter += 1 # Suma al contador
            if self.counter == 2: # Se asegura de que el sonido solo se active una vez y casi al instante de pasar el mouse por encima 
                sounds.check_sound.play() # Activa el sonido
        else:
            self.counter = 0 # Reinicia el contador
            self.tempcolor = self.backgroundColor #Vuelve a colocar el color temporal en su valor default

    # Obtiene coordendas y dimensiones de los botones
    def get_rect(self):
        x = self.x - self.w//2 - self.thickness//2
        y = self.y - self.h //2 - self.thickness//2
        w = self.w + self.thickness
        h = self.h + self.thickness
        return pygame.Rect(x, y, w, h)

    #Dibuja los botones
    def Draw(self):
        # Obtiene coordenadas y dimensiones del borde
        out_x = self.x - self.w//2 - self.thickness//2
        out_y = self.y - self.h //2 - self.thickness//2
        out_w = self.w + self.thickness
        out_h = self.h + self.thickness

        # Obtiene coordenadas y dimensiones del interior
        in_x = self.x - self.w //2
        in_y = self.y - self.h //2
        in_w = self.w
        in_h = self.h

        pygame.draw.rect(self.screen, self.outlineColor, [out_x, out_y, out_w, out_h]) # Dibuja el borde del boton
        pygame.draw.rect(self.screen, self.tempcolor, [in_x, in_y, in_w, in_h]) # Dibuja el interior del boton
        buttonText = self.font.render(self.text, True, self.textColor) # Define la fuente y el color del texto
        text_rect = buttonText.get_rect(center=(in_x + self.w//2, in_y + self.h//2)) # Obtiene las coordenadas para centrar el texto dentro del boton
        self.screen.blit(buttonText, text_rect) # Coloca el texto en las coordenadas obtenidas 

        self.Hover() # Ejecuta la revisión de si el mouse está encima de algún boton
