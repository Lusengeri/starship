import pygame
from pygame.locals import *
from vector2 import Vector2
import time
from random import randint

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
        starship = Starship(self, (SCREEN_SIZE[0]/2.0), (SCREEN_SIZE[1]-100))
        self.starship = starship
        self.game_objects.append(starship)
        for _ in range(10):
            meteor_speed = randint(400, 600) * 1.0
            x_location = randint(0, SCREEN_SIZE[0])
            meteor = Meteor(self, x_location, 0, meteor_speed)
            self.game_objects.append(meteor)

    def update(self, time_passed):
        for asset in self.game_objects:
            asset.update(time_passed)
            if asset.type == "meteor":
                if self.starship.rect.colliderect(asset.rect):
                    self.paused = True
                    display_game_over_screen(self.game_screen)

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
    def __init__(self, world, x_location = 0.0, y_location = 0.0):
        self.location = Vector2(x_location, y_location)
        self.world = world

    def render(self, surface):
        surface.blit(self.image, (self.location.x - self.image_w/2, self.location.y - self.image_h/2))

    def update(self, time_passed):
        self.heading.normalize()
        self.location +=  self.heading * self.speed * time_passed
        self.rect.center = ((self.location.x + self.image_w/2), (self.location.y + self.image_h/2))

class Starship(GameAsset):
    def __init__(self, world, x_location, y_location):
        super().__init__(world, x_location, y_location)
        self.image = pygame.image.load("images/starship.png").convert_alpha()
        self.image_w, self.image_h = self.image.get_size()
        self.speed = SPACECRAFT_SPEED 
        self.heading = Vector2(0.0, 0.0)
        self.type = "spaceship"
        self.rect = pygame.Rect(self.location.x, self.location.y, self.image_w, self.image_h)

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
    def __init__(self, world, x_location=0.0, y_location=0.0, speed=100.0):
        super().__init__(world, x_location, y_location)
        self.image = pygame.image.load("images/meteor.png").convert_alpha()
        self.image_w, self.image_h = self.image.get_size()
        self.speed = speed
        self.heading = Vector2(0.0, 1.0)
        self.type = "meteor"
        self.rect = pygame.Rect(self.location.x, self.location.y, self.image_w, self.image_h)

    def update(self, time_passed):
        super().update(time_passed)

        if self.location.y >= SCREEN_SIZE[1]:
            self.location.x = randint(0, SCREEN_SIZE[0])
            self.location.y = 0
            self.world.score += 1

def exit_procedure():
    pygame.quit()
    exit()

def display_intro_screen(surface):
    intro_screen_image = pygame.image.load(INTRO_SCREEN_FILE).convert_alpha()
    i_w, i_h = intro_screen_image.get_size()
    surface.blit(intro_screen_image, ((SCREEN_SIZE[0]/2)-(i_w/2), (SCREEN_SIZE[1]/2)-(i_h/2)))
    pygame.display.update()
    time.sleep(3)
    display_game_menu(surface)

def display_exit_prompt(surface):
    surface.fill((0, 0, 0, 0.5))
    question = "Are you sure you want to exit?"
    options = "Yes / No"
    question_font = pygame.font.SysFont("inconsolata", 32)
    options_font = pygame.font.SysFont("inconsolata", 24)
    question_surface = question_font.render(question, True, WHITE, BLACK)
    options_surface = options_font.render(options, True, WHITE, BLACK)
    q_w, q_h = question_surface.get_size()
    surface.blit(question_surface, (SCREEN_SIZE[0]/2 - q_w/2,  SCREEN_SIZE[1]/2))
    surface.blit(options_surface, (SCREEN_SIZE[0]/2 - q_w/2 + 120,  SCREEN_SIZE[1]/2 + 40))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_y:
                    exit_procedure()
                elif event.key == K_n:
                    return

def display_about_menu(surface):
    surface.fill((0, 0, 0, 0.5))
    title_font = pygame.font.SysFont("inconsolata", 32, bold=True)
    title_surface = title_font.render("About Starship Odyssey", True, WHITE, BLACK)
    title_width, title_height = title_surface.get_size()
    surface.blit(title_surface, (SCREEN_SIZE[0]/2 - title_width/2, SCREEN_SIZE[1]/2 - 50))
    text_font = pygame.font.SysFont("inconsolata", 16)

    about_file = open("README.md", "r", 1)
    
    for line in about_file:
        text_surface = text_font.render(line, True, WHITE, BLACK)
        text_width, text_height = text_surface.get_size()
        surface.blit(text_surface, (40, SCREEN_SIZE[1]/2))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    about_file.close()
                    return

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
                    print()
                elif event.key == K_a:
                    display_about_menu(surface)
                elif event.key == K_ESCAPE:
                    display_exit_prompt(surface)

        pygame.display.update()

def display_game_over_screen(surface):
    surface.fill((0, 0, 0, 0.5))
    title_font = pygame.font.SysFont("inconsolata", 32, bold=True)
    title_surface = title_font.render("Game Over!", True, WHITE, BLACK)
    title_width, title_height = title_surface.get_size()
    surface.blit(title_surface, (SCREEN_SIZE[0]/2 - title_width/2, SCREEN_SIZE[1]/2 - 50))
    text_font = pygame.font.SysFont("inconsolata", 28)
    text_surface = text_font.render("Collision", True, WHITE, BLACK)
    text_width, text_height = text_surface.get_size()
    surface.blit(text_surface, (SCREEN_SIZE[0]/2 -text_width/2, SCREEN_SIZE[1]/2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return

def main():
    #Initialize game environment
    pygame.init()
    display_surface = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN)
    pygame.mouse.set_visible(False)
    #Start the game with splash creen
    display_intro_screen(display_surface)
    #display_game_menu(display_surface)

if __name__ == "__main__":
    main()
