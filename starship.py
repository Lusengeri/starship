import pygame
from pygame.locals import *
from vector2 import Vector2
from random import randint
import time
import csv
import os
from pathlib import Path

SCREEN_SIZE = (1366, 768)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPACECRAFT_SPEED = 400

INTRO_SCREEN_FILE = "images/SplashScreenImage.png"
PLAYER_DATA_FILE = "user_data/player_data.csv"
HIGH_SCORE_FILE = "user_data/high_scores.csv" 
ABOUT_FILE = "README.md"

def sync_player_list(new_player_list = None):
            if not new_player_list is None:          
                with open(PLAYER_DATA_FILE, "w") as player_data_file:
                    if len(new_player_list) == 0:
                        player_data_file.truncate(0)
                    else:
                        field_names = ["name", "score"]
                        writer = csv.DictWriter(player_data_file, fieldnames=field_names)
                        for row in new_player_list:
                            writer.writerow({"name": row[0], "score": row[1]})

            player_list = []

            if os.path.exists(PLAYER_DATA_FILE):
                with open(PLAYER_DATA_FILE, "r") as player_data_file:
                    reader = csv.reader(player_data_file)
                    for row in reader:
                        player_name = row[0]
                        high_score = int(row[1])
                        player_list.append([player_name, high_score])
            
            return player_list

class GameData():
    def __init__(self, screen, player_list):
       self.screen = screen 
       self.player_list = player_list
       self.current_player = Player("No Player", 0)

class MenuStateMachine(object):
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, 32)
        player_list = sync_player_list() 
        self.game_data = GameData(screen, player_list)

        #Set-up user-data files
        if not os.path.isdir("user_data"):
            os.mkdir("user_data")

        Path(PLAYER_DATA_FILE).touch()
        Path(HIGH_SCORE_FILE).touch()

        self.states = {'splash_screen' : SplashScreenState('splash_screen', self.game_data), 'game_menu' : GameMenuState('game_menu', self.game_data), 'choose_player':ChoosePlayerState('choose_player', self.game_data), 'about_menu':AboutMenuState('about_menu', self.game_data), 'exit_confirm': ExitConfirmState('exit_confirm', self.game_data), 'create_player':CreatePlayerState('create_player', self.game_data), 'game_play': GamePlayState('game_play', self.game_data), 'pause_screen': PauseScreenState('pause_screen', self.game_data), 'game_result':GameResultState('game_result', self.game_data)}

        self.active_state = self.states['splash_screen']
    
    def add_state(self, state): #Why???
        self.states[state.name] = state

    def process(self):
        while 1:
            if self.active_state is None:
                return

            self.active_state.do_actions()
            
            new_state_name = self.active_state.check_conditions()

            if new_state_name is not None:
                if self.active_state.name == "game_play" and new_state_name == "game_result":
                    self.states['game_result'].score = self.active_state.current_score
                self.set_state(new_state_name)

    def set_state(self, new_state_name):
        if self.active_state is not None:
            self.active_state.exit_actions()

        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()

class Player(object):
    def __init__(self, name, highest_score):
        self.name = name
        self.high_score = highest_score

class GameState(object):
    def __init__(self, name, game_data):
        self.name = name
        self.player_list = game_data.player_list
        self.screen = game_data.screen
        self.current_player = game_data.current_player

    def do_actions(self):
        pass

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass

class SplashScreenState(GameState):
    def do_actions(self): 
        self.screen.fill(BLACK)
        intro_screen_image = pygame.image.load(INTRO_SCREEN_FILE).convert_alpha()
        i_w, i_h = intro_screen_image.get_size()
        self.screen.blit(intro_screen_image, ((SCREEN_SIZE[0]/2)-(i_w/2), (SCREEN_SIZE[1]/2)-(i_h/2)))
        pygame.display.update()
        time.sleep(3)

    def check_conditions(self):
        return "choose_player"

class ChoosePlayerState(GameState):
    def __init__(self, name, game_data):
        super().__init__(name, game_data)
        self.list_size = len(self.player_list)
        self.highlight_index = 0

    def do_actions(self):
        self.screen.fill(BLACK)
        #Create the text to display the options available
        title_font = pygame.font.SysFont("Inconsolata", 32)
        list_font = pygame.font.SysFont("inconsolata", 24)

        title1_surface = title_font.render("SELECT A PLAYER", True, WHITE, BLACK)
        title2_surface = title_font.render("TO CREATE A NEW PLAYER\n (press C)", True, WHITE, BLACK)
        title3_surface = title_font.render("TO DELETE A PLAYER\n (press X)", True, WHITE, BLACK)

        #Retrieve the list of players from file
        self.list_size = len(self.player_list)

        self.screen.fill(BLACK)
        self.screen.blit(title1_surface, (SCREEN_SIZE[0]/2 - 400, 200))
        self.screen.blit(title2_surface, (SCREEN_SIZE[0]/2 - 400, 250))
        self.screen.blit(title3_surface, (SCREEN_SIZE[0]/2 - 400, 300))

        count = 0
        for player in self.player_list:
            if player[0] == self.player_list[self.highlight_index][0]:
                FORE = BLACK
                BACK = WHITE
            else:
                FORE = WHITE
                BACK = BLACK

            name_surface = list_font.render(player[0], True, FORE, BACK)
            self.screen.blit(name_surface, (SCREEN_SIZE[0]/2 - 400, 350 +(count*36)))
            count += 1

        pygame.display.update()

    def check_conditions(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN: 
                    if event.key == K_RETURN:
                        if self.list_size > 0:
                            self.current_player.name = self.player_list[self.highlight_index][0]
                            self.current_player.high_score = int(self.player_list[self.highlight_index][1])
                            return "game_menu"
                    elif event.key == K_DOWN:
                        if not self.highlight_index == (self.list_size-1):
                            self.highlight_index += 1
                        return None
                    elif event.key == K_UP:
                        if not self.highlight_index == 0:
                            self.highlight_index -= 1
                        return None
                    elif event.key == K_c:
                        return "create_player"
                    elif event.key == K_x:
                        if len(self.player_list) > 0:
                            self.player_list.pop(self.highlight_index)
                            self.player_list = self.sync_player_list(self.player_list)
                            self.list_size = len(self.player_list)
                            self.highlight_index = 0
                            return None

    def entry_actions(self):
        self.player_list = sync_player_list()
        self.list_size = len(self.player_list)
        self.highlight_index = 0

class CreatePlayerState(GameState):
    def __init__(self, name, game_data):
        super().__init__(name, game_data)
        self.name_string = ""
 
    def do_actions(self):
        self.screen.fill(BLACK)

        title_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        name_font = pygame.font.SysFont("inconsolata", 28)
        title_text = "Please enter the name of the new player:"
        title_surface = title_font.render(title_text, True, WHITE, BLACK)
       
        name_surface = name_font.render(self.name_string, True, BLACK, WHITE)
        self.screen.blit(name_surface, (SCREEN_SIZE[0]/2 - 200, SCREEN_SIZE[1]/2 - 100))
        self.screen.blit(title_surface, (SCREEN_SIZE[0]/2 - 200, SCREEN_SIZE[1]/2 - 200))
        pygame.display.update()

    def check_conditions(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return "choose_player"
                    elif event.key == K_BACKSPACE:
                        strlen = len(self.name_string)
                        self.name_string = self.name_string[:(strlen-1)]
                        return None
                    elif event.key == K_RETURN:
                        if len(self.name_string) > 0:
                            with open(PLAYER_DATA_FILE, "a") as player_data_file:
                                field_names = ["name", "score"]
                                writer = csv.DictWriter(player_data_file, fieldnames=field_names)
                                writer.writerow({"name": self.name_string, "score": 0})
         
                            #self.player_list = self.sync_player_list()          
                            return "choose_player"
                    else:
                        self.name_string += event.unicode
                        return None

    def entry_actions(self):
        self.name_string = ""

    def exit_actions(self):
        self.player_list = sync_player_list() 

class GameMenuState(GameState):
    def do_actions(self):
        start_game_text = "New Game"
        change_player_text = "Change Player"
        high_score_text = "High-Score Table"
        about_text = "About"

        text_font = pygame.font.Font("freesansbold.ttf", 24)

        text1_surface = text_font.render(start_game_text, True, WHITE, BLACK)
        text2_surface = text_font.render(about_text, True, WHITE, BLACK)
        text3_surface = text_font.render(high_score_text, True, WHITE, BLACK)
        text4_surface = text_font.render(change_player_text, True, WHITE, BLACK)
        
        text1_rectangle = text1_surface.get_rect()
        text2_rectangle = text2_surface.get_rect()
        text3_rectangle = text3_surface.get_rect()
        text4_rectangle = text4_surface.get_rect()
        
        text1_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3)
        text2_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3 + 32)
        text3_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3 + 64)
        text4_rectangle.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3 + 96)

        self.screen.fill(BLACK)
        self.screen.blit(text1_surface, text1_rectangle)
        self.screen.blit(text2_surface, text2_rectangle)
        self.screen.blit(text3_surface, text3_rectangle)
        self.screen.blit(text4_surface, text4_rectangle)

        pygame.display.update()

    def check_conditions(self):
        while 1 :
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_n:
                        return "game_play"
                    elif event.key == K_h:
                        #return "high_scores"
                        return "splash_screen"
                    elif event.key == K_a:
                        return "about_menu"
                    elif event.key == K_c:
                        return "choose_player"
                    elif event.key == K_ESCAPE:
                        return "exit_confirm"
                    
class AboutMenuState(GameState):
    def __init__(self, name, game_data):
        super().__init__(name, game_data)
        self.about_file = open(ABOUT_FILE, "r", 1)

    def do_actions(self):
        self.screen.fill((0, 0, 0, 0.5))
        title_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        title_surface = title_font.render("About Starship Odyssey", True, WHITE, BLACK)
        title_width, title_height = title_surface.get_size()
        self.screen.blit(title_surface, (SCREEN_SIZE[0]/2 - title_width/2, SCREEN_SIZE[1]/2 - 50))
        text_font = pygame.font.SysFont("inconsolata", 16)

        for line in self.about_file:
            text_surface = text_font.render(line, True, WHITE, BLACK)
            text_width, text_height = text_surface.get_size()
            self.screen.blit(text_surface, (40, SCREEN_SIZE[1]/2))

        pygame.display.update()

    def check_conditions(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return "game_menu"

    def entry_actions(self):
        self.about_file = open(ABOUT_FILE, "r", 1)

    def exit_actions(self):
        self.about_file.close()

class ExitConfirmState(GameState):
    def do_actions(self):
        self.screen.fill((0, 0, 0, 0.5))
        question = "Are you sure you want to exit?"
        options = "Yes / No"
        question_font = pygame.font.SysFont("inconsolata", 32)
        options_font = pygame.font.SysFont("inconsolata", 24)
        question_surface = question_font.render(question, True, WHITE, BLACK)
        options_surface = options_font.render(options, True, WHITE, BLACK)
        q_w, q_h = question_surface.get_size()
        self.screen.blit(question_surface, (SCREEN_SIZE[0]/2 - q_w/2,  SCREEN_SIZE[1]/2))
        self.screen.blit(options_surface, (SCREEN_SIZE[0]/2 - q_w/2 + 120,  SCREEN_SIZE[1]/2 + 40))
        pygame.display.update()
        
    def check_conditions(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_y:
                        pygame.quit()
                        exit()
                    elif event.key == K_n:
                        return "game_menu"

class GamePlayState(GameState):
    def __init__(self, name, game_data):
        super().__init__(name, game_data)
        self.game_state = "not_running"
        self.reset_game()

    def reset_game(self):
        self.current_score = 0
        self.game_objects = []
        starship = Starship(self, (SCREEN_SIZE[0]/2.0), (SCREEN_SIZE[1]-100))
        self.starship = starship
        self.game_objects.append(starship)

        for _ in range(10):
            meteor_speed = randint(800, 1000) * 1.0
            x_location = randint(0, SCREEN_SIZE[0])
            meteor = Meteor(self, x_location, 0, meteor_speed)
            self.game_objects.append(meteor)

        self.clock = pygame.time.Clock()

    def do_actions(self):
        #Draw all game artifacts here
        self.screen.fill(BLACK)
        for asset in self.game_objects:
            asset.render(self.screen)

        self.display_score()
        self.display_player_stats()
        pygame.display.update()

    def display_score(self):
        score_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        score_surface = score_font.render("SCORE:" + str(self.current_score), True, WHITE, BLACK)
        self.screen.blit(score_surface, (0, 0))

    def display_player_stats(self):
        player_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        player_surface = player_font.render("PLAYER: " + str(self.current_player.name) + " HIGH SCORE: " + str(self.current_player.high_score), True, WHITE, BLACK)
        self.screen.blit(player_surface, (0, 40))

    def check_conditions(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game_state = "paused"
                        return "pause_screen"

            time_passed = self.clock.tick()/1000.0
            return self.update(time_passed)

    def update(self, time_passed):
        for asset in self.game_objects:
            asset.update(time_passed)
            if asset.type == "meteor":
                if self.starship.rect.colliderect(asset.rect):
                    ##if self.player.high_score < self.score:
                        ##self.player.high_score = self.score
                    self.game_state = "not_running"
                    return "game_result"
        return None

    def entry_actions(self):
        #Show countdown timer to start the spaceship
        if self.game_state == "not_running":
            self.reset_game()
            self.game_state = "running"
            #Start clock
        elif self.game_state == "paused":
            print('Do Nothing')
            #Resume Clock

    def exit_actions(self):
        pass
        #Pause Clock
        
class GameResultState(GameState):
    def __init__(self, name, game_data):
        super().__init__(name, game_data)
        self.score = None

    def do_actions(self):
        self.screen.fill((0, 0, 0, 0.5))
        title_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        title_surface = title_font.render("Game Over!", True, WHITE, BLACK)
        title_width, title_height = title_surface.get_size()
        self.screen.blit(title_surface, (SCREEN_SIZE[0]/2 - title_width/2, SCREEN_SIZE[1]/2 - 50))
        text_font = pygame.font.SysFont("inconsolata", 28)
        text_surface = text_font.render("Collision", True, WHITE, BLACK)
        text_width, text_height = text_surface.get_size()
        self.screen.blit(text_surface, (SCREEN_SIZE[0]/2 -text_width/2, SCREEN_SIZE[1]/2))
        score_surface = text_font.render("Your Score: " + str(self.score), True, WHITE, BLACK)
        score_width, score_height = score_surface.get_size()
        self.screen.blit(score_surface, (SCREEN_SIZE[0]/2 -score_width/2, SCREEN_SIZE[1]/2 + score_height))
        pygame.display.update()

    def check_conditions(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return "game_menu"

    def _exit_actions(self):
        #Save game result to high-score/ personal-best file if required
        index = 0
        for player in self.player_list:
            if player[0] == game_result.name:
                if game_result.high_score > self.player_list[index][1]:
                    self.player_list[index][1] = game_result.high_score
            index += 1

        self.player_list = sync_player_list(self.player_list)

class PauseScreenState(GameState):
    def do_actions(self):
        symbol = "||"
        text = "PAUSED"
        font = pygame.font.SysFont("inconsolata", 64)
        symbol_surface = font.render(symbol, True, WHITE, BLACK)
        text_surface = font.render(text, True, WHITE, BLACK)
        self.screen.blit(symbol_surface, (SCREEN_SIZE[0]/2-25, SCREEN_SIZE[1]/2-100))
        self.screen.blit(text_surface, (SCREEN_SIZE[0]/2-65, SCREEN_SIZE[1]/2))
        pygame.display.update()

    def check_conditions(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return "game_play"
                    #Provide facility for quiting game
                    #elif event.key == K_RETURN:
                        #return
            return None

class GameAsset(object):
    def __init__(self, world, x_location = 0.0, y_location = 0.0):
        self.world = world
        self.location = Vector2(x_location, y_location)

    def render(self, surface):
        surface.blit(self.image, (self.location.x - self.image_w/2, self.location.y - self.image_h/2))

    def update(self, time_passed):
        self.heading.normalize()
        self.location +=  self.heading * self.speed * time_passed
        self.rect.center = ((self.location.x + self.image_w/2), (self.location.y + self.image_h/2))

    def load_image(self, filename):
        self.image = pygame.image.load(filename).convert_alpha()
        self.image_w, self.image_h = self.image.get_size()
        self.rect = pygame.Rect(self.location.x, self.location.y, self.image_w, self.image_h)

class Starship(GameAsset):
    def __init__(self, world, x_location, y_location):
        super().__init__(world, x_location, y_location)
        self.heading = Vector2(0.0, 0.0)
        self.load_image("images/craft.png")
        self.speed = SPACECRAFT_SPEED 
        self.type = "spaceship"

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
        self.heading = Vector2(0.0, 1.0)
        self.load_image("images/meteor.png")
        self.speed = speed
        self.type = "meteor"

    def update(self, time_passed):
        super().update(time_passed)

        if self.location.y >= SCREEN_SIZE[1]:
            self.location.x = randint(0, SCREEN_SIZE[0])
            self.location.y = 0
            #self.world.score += 1
            self.world.current_score += 1
    
if __name__ == "__main__":
    app = MenuStateMachine()
    app.process()
