import pygame
import sys

# Initialiser Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Netflix-Style Intro")

# Couleurs
BLACK = (0, 0, 0)

# Charger l'image du logo "N"
logo = pygame.image.load("logo.png")  # Remplace "logo.png" par ton fichier
logo = pygame.transform.scale(logo, (100, 200))  # Taille initiale du logo

# Charger la musique d'intro
pygame.mixer.music.load("millenium-206201.mp3")  
pygame.mixer.music.play()

# Variables pour l'animation
scale_factor = 0.1
logo_pos = [WIDTH // 2, HEIGHT // 2]
running = True

# Boucle principale
while running:
    screen.fill(BLACK)  # Fond noir

    # Événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Agrandir le logo
    if scale_factor < 1.5:  # Limiter la taille du logo
        scale_factor += 0.01
        new_width = int(100 * scale_factor)
        new_height = int(200 * scale_factor)
        scaled_logo = pygame.transform.scale(logo, (new_width, new_height))
        logo_pos = [WIDTH // 2 - new_width // 2, HEIGHT // 2 - new_height // 2]
        screen.blit(scaled_logo, logo_pos)

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Limiter la vitesse d'animation
    pygame.time.Clock().tick(60)

# Quitter proprement
pygame.quit()
sys.exit()