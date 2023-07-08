import pygame
import sys
from setting import Config
from screens.menu import Menu

def main():
    # Inicializar Pygame
    pygame.init()   
    pygame.font.init()
    screen = pygame.display.set_mode(Config.resolution)

    # Cargar y colocar un icono en la pantalla principal
    loaded_icon = pygame.image.load("./assets/images/white_knight.png")
    main_icon = pygame.transform.smoothscale(loaded_icon, (Config.windowIconSize, Config.windowIconSize))
    pygame.display.set_icon(main_icon)
    # Le coloca nombre a la ventana
    pygame.display.set_caption("Chess")
    # Loop del juego
    MenuScreen = Menu(screen)
    MenuScreen.Run()
    # cerrar Pygame 
    pygame.quit()
    sys.exit()

# Asegura que el código dentro del bloque solo se ejecute si el script se ejecuta directamente y no al importarse como un módulo.
if __name__ == "__main__":
    main()
