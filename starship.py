import pygame
from pygame.locals import *
from vector2 import Vector2
import time

SCREEN_SIZE = (1366, 768)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPACECRAFT_SPEED = 400
INTRO_SCREEN_FILE = "images/SplashScreenImage.png"

class Player(object):
    def __init__(self, name, highest_score):
        self.name = name
        self.high_score = highest_score
        #self.image = image

class Game(object):
    def __init__(self, player, game_screen):
        self.player = player
        self.game_screen = game_screen
        self.paused = False
        self.game_objects = []
        self.score = 0
        self.clock = pygame.time.Clock()
        self.initialize_assets()

    def initialize_assets(self):
        starship = Starship((SCREEN_SIZE[0]/2.0), (SCREEN_SIZE[1]-100))
        self.game_objects.append(starship)

    def update(self, time_passed):
        for asset in self.game_objects:
            asset.update(time_passed)

    def render(self):
        #Draw all game artifacts here
        for asset in self.game_objects:
            asset.render(self.game_screen)

    def play(self):
        self.paused = False
        while not self.paused:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        #self.paused = True
                        return 
                     
            self.game_screen.fill(BLACK)
            time_passed = self.clock.tick()/1000.0
            self.update(time_passed)
            self.render()
            pygame.display.update()

class GameAsset(object):
    def __init__(self, x_location = 0.0, y_location = 0.0):
        self.location = Vector2(x_location, y_location)
        self.heading = Vector2(0, 0)

    def render(self, surface):
        surface.blit(self.image, (self.location.x - self.image_w/2, self.location.y - self.image_h/2))

    def update(self, time_passed):
        self.heading.normalize()
        self.location +=  self.heading * self.speed * time_passed
   
class Starship(GameAsset):
    def __init__(self, x_location, y_location):
        super().__init__(x_location, y_location)
        self.image = pygame.image.load("images/starship.png").convert_alpha()
        self.image_w, self.image_h = self.image.get_size()
        self.speed = SPACECRAFT_SPEED 

    def update(self, time_passed):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.heading.x = -1.0
        elif pressed_keys[K_RIGHT]:
            self.heading.x = 1.0
        else:
            self.heading.x = 0.0

        if pressed_keys[K_UP]:
            self.heading.y = -1.0
        elif pressed_keys[K_DOWN]:
            self.heading.y = 1.0
        else:
            self.heading.y = 0.0
        
        super().update(time_passed)

        if self.location.x < self.image_w/2:
            self.location.x = self.image_w/2 
        elif self.location.x > SCREEN_SIZE[0] - self.image_w/2:
            self.location.x = SCREEN_SIZE[0]- self.image_w/2

        if self.location.y > SCREEN_SIZE[1] - self.image_h:
            self.location.y = SCREEN_SIZE[1] - self.image_h
        elif self.location.y < self.image_h:
            self.location.y = self.image_h

class Meteor(GameAsset):
    pass

def exit_procedure(surface):
    pygame.quit()
    exit()

def display_intro_screen(surface):
    intro_screen_image = pygame.image.load(INTRO_SCREEN_FILE).convert_alpha()
    i_w, i_h = intro_screen_image.get_size()
    surface.blit(intro_screen_image, ((SCREEN_SIZE[0]/2)-(i_w/2), (SCREEN_SIZE[1]/2)-(i_h/2)))
    pygame.display.update()
    time.sleep(3)

def display_game_menu(surface):
    running = True
    while running:
        start_game_text = "New Game"
        high_score_text = "High-Score Table"
        about_text = "About"
        text_font = pygame.font.Font("freesansbold.ttf", 24)
        text1_surface = text_font.render(start_game_text, True, WHITE, BLACK)
        text2_surface = text_font.render(high_score_text, True, WHITE, BLACK)
        text3_surface = text_font.render(about_text, True, WHITE, BLACK)
        text1_rectangle = text1_surface.get_rect()
        text2_rectangle = text2_surface.get_rect()
        text3_rectangle = text3_surface.get_rect()
        text1_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3)
        text2_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3 + 32)
        text3_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3 + 64)
        surface.fill(BLACK)
        surface.blit(text1_surface, text1_rectangle)
        surface.blit(text2_surface, text2_rectangle)
        surface.blit(text3_surface, text3_rectangle)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_n:
                    #Start a game
                    player = Player("Moses", 0)
                    new_game = Game(player, surface)
                    new_game.play()
                elif event.key == K_h:
                    #Display high-score table
                elif event.key == K_a:
                    #Display about menu
                elif event.key == K_ESCAPE:
                    exit_procedure(surface)
        pygame.display.update()

def main():
    #Initialize game environment
    pygame.init()
    display_surface = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN)
    pygame.mouse.set_visible(False)
    #Display the game splash creen
    display_intro_screen(display_surface)
    #Open game menu
    display_game_menu(display_surface)

if __name__ == "__main__":
    main()
