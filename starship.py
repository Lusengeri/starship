import pygame
from pygame.locals import *
from vector2 import Vector2
from random import randint
import time
import csv

SCREEN_SIZE = (1366, 768)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPACECRAFT_SPEED = 400
INTRO_SCREEN_FILE = "images/SplashScreenImage.png"

class GameApp():
        pass

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
            meteor_speed = randint(800, 1000) * 1.0
            x_location = randint(0, SCREEN_SIZE[0])
            meteor = Meteor(self, x_location, 0, meteor_speed)
            self.game_objects.append(meteor)

    def update(self, time_passed):
        for asset in self.game_objects:
            asset.update(time_passed)
            if asset.type == "meteor":
                if self.starship.rect.colliderect(asset.rect):
                    self.paused = True
                    self.update_user_data()
                    self.display_game_over_screen()
    
    def update_user_data(self):
        player_list = get_player_list()     
        for item in player_list:
            if item[0] == self.player.name:
                if int(item[1]) < self.score:
                    self.player.high_score = self.score
                    item[1] = str(self.score)

        update_player_list(player_list)

    def render(self):
        #Draw all game artifacts here
        for asset in self.game_objects:
            asset.render(self.game_screen)

        self.display_score()
        self.display_player_stats()

    def display_score(self):
        score_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        score_surface = score_font.render("SCORE:" + str(self.score), True, WHITE, BLACK)
        self.game_screen.blit(score_surface, (0, 0))

    def display_player_stats(self):
        player_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        player_surface = player_font.render("PLAYER: " + str(self.player.name) + " HIGH SCORE: " + str(self.player.high_score), True, WHITE, BLACK)
        self.game_screen.blit(player_surface, (0, 40))

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

    def display_game_over_screen(self):
        self.game_screen.fill((0, 0, 0, 0.5))
        title_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        title_surface = title_font.render("Game Over!", True, WHITE, BLACK)
        title_width, title_height = title_surface.get_size()
        self.game_screen.blit(title_surface, (SCREEN_SIZE[0]/2 - title_width/2, SCREEN_SIZE[1]/2 - 50))
        text_font = pygame.font.SysFont("inconsolata", 28)
        text_surface = text_font.render("Collision", True, WHITE, BLACK)
        text_width, text_height = text_surface.get_size()
        self.game_screen.blit(text_surface, (SCREEN_SIZE[0]/2 -text_width/2, SCREEN_SIZE[1]/2))
        score_surface = text_font.render("Your Score: " + str(self.score), True, WHITE, BLACK)
        score_width, score_height = score_surface.get_size()
        self.game_screen.blit(score_surface, (SCREEN_SIZE[0]/2 -score_width/2, SCREEN_SIZE[1]/2 + score_height))
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return

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
    display_player_selection(surface)

def get_player_list():
    player_list = []
    with open("user_data/player_data.csv") as player_data_file:
        reader = csv.reader(player_data_file)
        for row in reader:
            player_name = row[0]
            high_score = row[1]
            player_list.append([player_name, high_score])
    
    return player_list

def update_player_list(new_player_list):
    with open("user_data/player_data.csv", "w") as player_data_file:
        field_names = ["name", "score"]
        writer = csv.DictWriter(player_data_file, fieldnames=field_names)
        for row in new_player_list:
            writer.writerow({"name": row[0], "score": row[1]})

def display_player_selection(surface):
    #Clear the screen
    surface.fill(BLACK)

    #Create the text to display the options available
    title_font = pygame.font.SysFont("Inconsolata", 32)
    title1_surface = title_font.render("SELECT A PLAYER", True, WHITE, BLACK)
    title2_surface = title_font.render("TO CREATE A NEW PLAYER\n (press C)", True, WHITE, BLACK)
    title3_surface = title_font.render("TO DELETE A PLAYER\n (press X)", True, WHITE, BLACK)
    list_font = pygame.font.SysFont("inconsolata", 24)

    #Retrieve the list of players from file
    player_list = get_player_list()
    list_size = len(player_list)
    highlight_index = 0 

    #Listen for user input: Select player, Create new player, Delete Player
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN: 
                if event.key == K_RETURN:
                    player = Player(player_list[highlight_index][0], player_list[highlight_index][1])
                    display_game_menu(surface, player)
                elif event.key == K_DOWN:
                    if not highlight_index == (list_size-1):
                        highlight_index += 1
                elif event.key == K_UP:
                    if not highlight_index == 0:
                        highlight_index -= 1
                elif event.key == K_c:
                    display_create_player_menu(surface)
                    player_list = get_player_list() 
                    list_size = len(player_list)
                    highlight_index = 0
                elif event.key == K_x:
                    del player_list[highlight_index]
                    update_player_list(player_list)
                    player_list = get_player_list()
                    list_size = len(player_list)
                    highlight_index = 0

        surface.fill(BLACK)
        surface.blit(title1_surface, (SCREEN_SIZE[0]/2 - 400, 200))
        surface.blit(title2_surface, (SCREEN_SIZE[0]/2 - 400, 250))
        surface.blit(title3_surface, (SCREEN_SIZE[0]/2 - 400, 300))

        count = 0
        for name in player_list:
            if name[0] == player_list[highlight_index][0]:
                FORE = BLACK
                BACK = WHITE
            else:
                FORE = WHITE
                BACK = BLACK

            name_surface = list_font.render(name[0], True, FORE, BACK)
            surface.blit(name_surface, (SCREEN_SIZE[0]/2 - 400, 350 +(count*36)))
            count += 1

        pygame.display.update()

def display_create_player_menu(surface):
    surface.fill(BLACK)
    title_font = pygame.font.SysFont("inconsolata", 32, bold=True)
    name_font = pygame.font.SysFont("inconsolata", 28)
    title_text = "Please enter the name of the new player:"
    title_surface = title_font.render(title_text, True, WHITE, BLACK)
   
    pygame.display.update()
    name_string = ""
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_BACKSPACE:
                    strlen = len(name_string)
                    name_string = name_string[:(strlen-1)]
                elif event.key == K_RETURN:
                    if len(name_string) > 0:
                        with open("user_data/player_data.csv", "a") as player_data_file:
                            field_names = ["name", "score"]
                            writer = csv.DictWriter(player_data_file, fieldnames=field_names)
                            writer.writerow({"name": name_string, "score": 0})
                        
                        return
                else:
                    name_string += event.unicode

        surface.fill(BLACK)
        name_surface = name_font.render(name_string, True, BLACK, WHITE)
        surface.blit(name_surface, (SCREEN_SIZE[0]/2 - 200, SCREEN_SIZE[1]/2 - 100))
        surface.blit(title_surface, (SCREEN_SIZE[0]/2 - 200, SCREEN_SIZE[1]/2 - 200))
        pygame.display.update()
        
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

def display_game_menu(surface, player):
    running = True
    while running:
        start_game_text = "New Game"
        change_player_text = "Change Player"
        high_score_text = "High-Score Table"
        about_text = "About"
        text_font = pygame.font.Font("freesansbold.ttf", 24)
        text1_surface = text_font.render(start_game_text, True, WHITE, BLACK)
        text2_surface = text_font.render(high_score_text, True, WHITE, BLACK)
        text3_surface = text_font.render(about_text, True, WHITE, BLACK)
        text4_surface = text_font.render(change_player_text, True, WHITE, BLACK)
        text1_rectangle = text1_surface.get_rect()
        text2_rectangle = text2_surface.get_rect()
        text3_rectangle = text3_surface.get_rect()
        text4_rectangle = text4_surface.get_rect()
        text1_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3)
        text2_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3 + 32)
        text3_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3 + 64)
        text4_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3 + 96)
        surface.fill(BLACK)
        surface.blit(text1_surface, text1_rectangle)
        surface.blit(text2_surface, text2_rectangle)
        surface.blit(text3_surface, text3_rectangle)
        surface.blit(text4_surface, text4_rectangle)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_n:
                    #Start a game
                    new_game = Game(player, surface)
                    new_game.play()
                elif event.key == K_h:
                    display_high_score_table(surface)
                elif event.key == K_a:
                    display_about_menu(surface)
                elif event.key == K_c:
                    running = False 
                    break
                    display_player_selection(surface)
                elif event.key == K_ESCAPE:
                    display_exit_prompt(surface)

        pygame.display.update()

def display_high_score_table(surface):
    pass

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

if __name__ == "__main__":
    main()
