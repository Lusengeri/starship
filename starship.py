import pygame
import pygame_gui
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

class MenuStateMachine(object):
    def __init__(self):
        self.states =  {}
        self.active_state = None
    
    def add_state(self, state):
        self.states[state.name] = state

    def process(self):
        while 1:
            if self.active_state is None:
                return

            self.active_state.do_actions()
            
            new_state_name = self.active_state.check_conditions()

            if new_state_name is not None:
                self.set_state(new_state_name)

    def set_state(self, new_state_name):
        if self.active_state is not None:
            self.active_state.exit_actions()

        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()

def sync_player_list(new_list = None):
    return sync_list(PLAYER_DATA_FILE, new_list)

def sync_high_score_list(new_list = None):
    return sync_list(HIGH_SCORE_FILE, new_list)

def sync_list(source_file, new_player_list = None):
            if not new_player_list is None:          
                with open(source_file, "w") as player_data_file:
                    if len(new_player_list) == 0:
                        player_data_file.truncate(0)
                    else:
                        field_names = ["name", "score"]
                        writer = csv.DictWriter(player_data_file, fieldnames=field_names)
                        for row in new_player_list:
                            writer.writerow({"name": row[0], "score": row[1]})

            player_list = []

            if os.path.exists(source_file):
                with open(source_file, "r") as player_data_file:
                    reader = csv.reader(player_data_file)
                    for row in reader:
                        player_name = row[0]
                        high_score = int(row[1])
                        player_list.append([player_name, high_score])
            
            return player_list

class Player(object):
    def __init__(self, name, highest_score):
        self.name = name
        self.high_score = highest_score

class GameState(object):
    def __init__(self, name):
        self.name = name
        self.gui_manager = pygame_gui.UIManager(SCREEN_SIZE)

    def do_actions(self):
        pass

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass

class SplashScreenMenu(GameState):
    def do_actions(self):
        super().do_actions()
        GameApp.screen.fill(BLACK)
        intro_screen_image = pygame.image.load(INTRO_SCREEN_FILE).convert_alpha()
        i_w, i_h = intro_screen_image.get_size()
        GameApp.screen.blit(intro_screen_image, ((SCREEN_SIZE[0]/2)-(i_w/2), (SCREEN_SIZE[1]/2)-(i_h/2)))
        pygame.display.update()
        time.sleep(3)

    def check_conditions(self):
        return "select_player"

    def entry_actions(self):
        pygame.mouse.set_visible(False)

    def exit_actions(self):
        pygame.mouse.set_visible(True)


class SelectPlayerMenu(GameState):
    def __init__(self, name):
        super().__init__(name)
        self.time_delta = 0.0
        self.internal_clock = pygame.time.Clock()
        self.initialize_gui_elements()

    def initialize_gui_elements(self):
        pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((384, 100), (600, 40)), text="SELECT A PLAYER", manager=self.gui_manager )
        pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((384, 150), (600, 40)), text="TO CREATE A NEW PLAYER PRESS 'C'", manager=self.gui_manager )
        pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((384, 200), (600, 40)), text="TO DELETE A PLAYER PRESS 'X'", manager=self.gui_manager)

        my_list = []
        for item in GameApp.player_list:
            my_list.append(item[0])
            
        self.selection_list = pygame_gui.elements.ui_selection_list.UISelectionList(relative_rect= pygame.Rect((384,250), (600,300)), item_list= my_list, manager= self.gui_manager)

        self.delete_player_button = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((384, 550), (175, 40)), text="DELETE", manager=self.gui_manager)
        self.create_player_button = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((598, 550), (175, 40)), text="CREATE NEW", manager=self.gui_manager)
        self.continue_button = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((810, 550), (174, 40)), text="CONTINUE", manager=self.gui_manager)

    def refresh_gui_elements(self):
        my_list = []
        for item in GameApp.player_list:
            my_list.append(item[0])

        self.selection_list.set_item_list(my_list)

    def do_actions(self):
        if self.selection_list.get_single_selection() == None:
            self.delete_player_button.disable()
            self.continue_button.disable()
        else:
            self.delete_player_button.enable()
            self.continue_button.enable()
    
        GameApp.screen.fill(BLACK)
        self.time_delta = GameApp.game_clock.tick(60)/1000.0
        self.gui_manager.update(self.time_delta)
        self.gui_manager.draw_ui(GameApp.screen)
        pygame.display.update()

    def check_conditions(self):
        for event in pygame.event.get():
            self.gui_manager.process_events(event)
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    GameApp.current_player.name = self.selection_list.get_single_selection()
                    GameApp.current_player.high_score =  int([player[1] for player in GameApp.player_list if player[0] == GameApp.current_player.name][0])
                    return "main_menu"
                elif event.key == K_DOWN:
                    #Keyboard navigation desirable for selection-list
                    return None
                elif event.key == K_UP:
                    #Keyboard navigation desirable for selection-list
                    return None
                elif event.key == K_c:
                    return "create_player"
                elif event.key == K_x:
                    if len(GameApp.player_list) > 0:
                        [GameApp.player_list.remove(player) for player in GameApp.player_list if player[0] == self.selection_list.get_single_selection()]
                        GameApp.player_list = sync_player_list(GameApp.player_list)
                        self.refresh_gui_elements()
                        return None

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.continue_button:
                        GameApp.current_player.name = self.selection_list.get_single_selection()
                        GameApp.current_player.high_score =  int([player[1] for player in GameApp.player_list if player[0] == GameApp.current_player.name][0])
                        return "main_menu"
                    elif event.ui_element == self.delete_player_button:
                        if len(GameApp.player_list) > 0:
                            [GameApp.player_list.remove(player) for player in GameApp.player_list if player[0] == self.selection_list.get_single_selection()]
                            GameApp.player_list = sync_player_list(GameApp.player_list)
                            self.refresh_gui_elements()
                            return None
                    elif event.ui_element == self.create_player_button:
                        return "create_player"

    def entry_actions(self):
        GameApp.player_list = sync_player_list()
        self.highlight_index = 0
        self.refresh_gui_elements()

class CreatePlayerMenu(GameState):
    def __init__(self, name):
        super().__init__(name)
        self.time_delta = 0.0
        self.internal_clock = pygame.time.Clock()
        self.initialize_gui_elements()

    def initialize_gui_elements(self):
        pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((384, 100), (600, 40)), text="CREATE A NEW PLAYER", manager=self.gui_manager)
        self.text_box = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((384, 200), (600, 40)), manager=self.gui_manager)
        self.cancel_button = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((480, 350), (175, 40)), text="CANCEL", manager=self.gui_manager)
        self.save_button = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((700, 350), (175, 40)), text="SAVE", manager=self.gui_manager)

    def do_actions(self):
        if len(self.text_box.get_text()) <= 0:
            self.save_button.disable()
        else:
            self.save_button.enable()

        GameApp.screen.fill(BLACK)
        self.time_delta = GameApp.game_clock.tick(60)/1000.0
        self.gui_manager.update(self.time_delta)
        self.gui_manager.draw_ui(GameApp.screen)
        pygame.display.update()

    def check_conditions(self):
        for event in pygame.event.get():
            self.gui_manager.process_events(event)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "select_player"
                elif event.key == K_RETURN:
                    inp = self.text_box.get_text()
                    if len(inp) > 0:
                        with open(PLAYER_DATA_FILE, "a") as player_data_file:
                            field_names = ["name", "score"]
                            writer = csv.DictWriter(player_data_file, fieldnames=field_names)
                            writer.writerow({"name": inp, "score": 0})

                        return "select_player"
                    else:
                        return None 
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.cancel_button:
                        return "select_player"
                    elif event.ui_element == self.save_button:
                        inp = self.text_box.get_text()
                        if len(inp) > 0:
                            with open(PLAYER_DATA_FILE, "a") as player_data_file:
                                field_names = ["name", "score"]
                                writer = csv.DictWriter(player_data_file, fieldnames=field_names)
                                writer.writerow({"name": inp, "score": 0})
                            return "select_player"
                        else:
                            return None

    def entry_actions(self):
        self.text_box.set_text("")

    def exit_actions(self):
        GameApp.player_list = sync_player_list()

class MainMenu(GameState):
    def __init__(self, name):
        super().__init__(name)
        self.time_delta = 0.0
        self.internal_clock = pygame.time.Clock()
        self.initialize_gui_elements()

    def initialize_gui_elements(self):
        self.new_game_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 160), (600, 40)), text="NEW GAME", manager=self.gui_manager)
        self.change_plyr_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 210), (600, 40)), text="CHANGE PLAYER", manager=self.gui_manager)
        self.hi_scores_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 260), (600, 40)), text="HIGH SCORES", manager=self.gui_manager)
        self.about_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 310), (600, 40)), text="ABOUT", manager=self.gui_manager)
        self.exit_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 360), (600, 40)), text="EXIT", manager=self.gui_manager)

    def do_actions(self):
        self.time_delta = GameApp.game_clock.tick(60)/1000.0
        GameApp.screen.fill(BLACK)
        self.gui_manager.update(self.time_delta)
        self.gui_manager.draw_ui(GameApp.screen)
        pygame.display.update()

    def check_conditions(self):
        for event in pygame.event.get():
            self.gui_manager.process_events(event)
            if event.type == KEYDOWN:
                if event.key == K_n:
                    return "game_play"
                elif event.key == K_h:
                    return "high_scores"
                elif event.key == K_a:
                    return "about"
                elif event.key == K_c:
                    return "select_player"
                elif event.key == K_ESCAPE:
                    return "exit_confirm"
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.new_game_btn:
                        return "game_play"
                    elif event.ui_element == self.change_plyr_btn:
                        return "select_player"
                    elif event.ui_element == self.hi_scores_btn:
                        return "high_scores"
                    elif event.ui_element == self.about_btn:
                        return "about"
                    elif event.ui_element == self.exit_btn:
                        return "exit_confirm"

class HighScoresMenu(GameState):
    def __init__(self, name):
        super().__init__(name)
        self.time_delta = 0.0
        self.internal_clock = pygame.time.Clock()
        self.initialize_gui_elements()

    def initialize_gui_elements(self):
        self.title_label = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((383, 160), (600, 40)), text="HIGH SCORES", manager=self.gui_manager)
        self.back_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 550), (175, 40)), text="BACK", manager=self.gui_manager)

    def do_actions(self):
        self.time_delta = self.internal_clock.tick(60)/1000.0
        GameApp.screen.fill(BLACK)
        #Create the text to display the options available
        #title_font = pygame.font.SysFont("Inconsolata", 32)
        list_font = pygame.font.SysFont("inconsolata", 20)

        #title1_surface = title_font.render("HIGH SCORE TABLE", True, WHITE, BLACK)

        #GameApp.screen.blit(title1_surface, (SCREEN_SIZE[0]/2 - 400, 200))

        count = 0
        for player in GameApp.high_score_list:
            FORE = BLACK
            BACK = WHITE

            name_surface = list_font.render(player[0] + " - " + str(player[1]), True, FORE, BACK)
            GameApp.screen.blit(name_surface, (SCREEN_SIZE[0]/2 - 300, 230 +(count*30)))
            count += 1

        self.gui_manager.update(self.time_delta)
        self.gui_manager.draw_ui(GameApp.screen)
        pygame.display.update()

    def check_conditions(self):
        self.time_delta = GameApp.game_clock.tick(60)/1000.0
        for event in pygame.event.get():
            self.gui_manager.process_events(event)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "main_menu"
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.back_btn:
                        return "main_menu"

class AboutMenu(GameState):
    def __init__(self, name):
        super().__init__(name)

    def do_actions(self):
        GameApp.screen.fill((0, 0, 0, 0.5))
        title_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        title_surface = title_font.render("About Starship Odyssey", True, WHITE, BLACK)
        title_width, title_height = title_surface.get_size()
        GameApp.screen.blit(title_surface, (SCREEN_SIZE[0]/2 - title_width/2, SCREEN_SIZE[1]/2 - 50))
        text_font = pygame.font.SysFont("inconsolata", 16)

        line_pos = 0
        for line in self.about_file:
            text_surface = text_font.render(line, True, WHITE, BLACK)
            text_width, text_height = text_surface.get_size()
            GameApp.screen.blit(text_surface, (270, (SCREEN_SIZE[1]/2)+line_pos))
            line_pos +=15

        pygame.display.update()

    def check_conditions(self):
        while True:
            self.time_delta = GameApp.game_clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return "main_menu"

    def entry_actions(self):
        self.about_file = open(ABOUT_FILE, "r", 1)

    def exit_actions(self):
        self.about_file.close()

class ExitConfirmMenu(GameState):
    def do_actions(self):
        GameApp.screen.fill((0, 0, 0, 0.5))
        question = "Are you sure you want to exit?"
        options = "Yes / No"
        question_font = pygame.font.SysFont("inconsolata", 32)
        options_font = pygame.font.SysFont("inconsolata", 24)
        question_surface = question_font.render(question, True, WHITE, BLACK)
        options_surface = options_font.render(options, True, WHITE, BLACK)
        q_w, q_h = question_surface.get_size()
        GameApp.screen.blit(question_surface, (SCREEN_SIZE[0]/2 - q_w/2,  SCREEN_SIZE[1]/2))
        GameApp.screen.blit(options_surface, (SCREEN_SIZE[0]/2 - q_w/2 + 120,  SCREEN_SIZE[1]/2 + 40))
        pygame.display.update()
        
    def check_conditions(self):
        while True:
            self.time_delta = GameApp.game_clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_y:
                        pygame.quit()
                        exit()
                    elif event.key == K_n:
                        return "main_menu"

class GamePlayMenu(GameState):
    def __init__(self, name):
        super().__init__(name)
        #self.game_state = "not_running"
        self.reset_game()

    def reset_game(self):
        GameApp.current_score = 0
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
        #super().do_actions()
        #Draw all game artifacts here
        GameApp.screen.fill(BLACK)
        for asset in self.game_objects:
            asset.render(GameApp.screen)

        self.display_score()
        self.display_player_stats()
        pygame.display.update()

    def display_score(self):
        score_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        score_surface = score_font.render("SCORE:" + str(GameApp.current_score), True, WHITE, BLACK)
        GameApp.screen.blit(score_surface, (0, 0))

    def display_player_stats(self):
        player_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        player_surface = player_font.render("PLAYER: " + str(GameApp.current_player.name) + " HIGH SCORE: " + str(GameApp.current_player.high_score), True, WHITE, BLACK)
        GameApp.screen.blit(player_surface, (0, 40))

    def check_conditions(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    GameApp.game_state = "paused"
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
                    GameApp.game_state = "not_running"
                    return "game_result"
        return None

    def entry_actions(self):
        pygame.mouse.set_visible(False)
        #Show countdown timer to start the spaceship
        if GameApp.game_state == "not_running":
            self.reset_game()
            GameApp.game_state = "running"
            #Start clock
        elif GameApp.game_state == "paused":
            #Reset clocking
            self.clock.tick()

    def exit_actions(self):
        pygame.mouse.set_visible(True)
        
class GameResultMenu(GameState):
    def __init__(self, name):
        super().__init__(name)
        self.menu_message = "Game Over!"

    def do_actions(self):
        GameApp.screen.fill((0, 0, 0, 0.5))
        title_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        title_surface = title_font.render(self.menu_message, True, WHITE, BLACK)
        title_width, title_height = title_surface.get_size()
        GameApp.screen.blit(title_surface, (SCREEN_SIZE[0]/2 - title_width/2, SCREEN_SIZE[1]/2 - 50))
        text_font = pygame.font.SysFont("inconsolata", 28)
        text_surface = text_font.render("Collision", True, WHITE, BLACK)
        text_width, text_height = text_surface.get_size()
        GameApp.screen.blit(text_surface, (SCREEN_SIZE[0]/2 -text_width/2, SCREEN_SIZE[1]/2))
        score_surface = text_font.render("Your Score: " + str(GameApp.current_score), True, WHITE, BLACK)
        score_width, score_height = score_surface.get_size()
        GameApp.screen.blit(score_surface, (SCREEN_SIZE[0]/2 -score_width/2, SCREEN_SIZE[1]/2 + score_height))
        pygame.display.update()

    def check_conditions(self):
        while True:
            self.time_delta = GameApp.game_clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return "main_menu"

    def entry_actions(self):
        if GameApp.isHighScore():
            self.menu_message = "High Score!"
    
    def exit_actions(self):
        #Save game result to high-score/ personal-best file if required
        GameApp.update_high_scores(Player(GameApp.current_player.name, GameApp.current_score))
        GameApp.update_player_data(Player(GameApp.current_player.name, GameApp.current_score))
        if GameApp.current_score > GameApp.current_player.high_score:
            GameApp.current_player.high_score = GameApp.current_score 

class PauseScreenMenu(GameState):
    def do_actions(self):
        symbol = "||"
        text = "PAUSED"
        quit_option = "Quit"
        resume_option = "Resume"
        font = pygame.font.SysFont("inconsolata", 64)
        symbol_surface = font.render(symbol, True, WHITE, BLACK)
        text_surface = font.render(text, True, WHITE, BLACK)
        quit_surface = font.render(quit_option, True, WHITE, BLACK)
        resume_surface = font.render(resume_option, True, WHITE, BLACK)
        GameApp.screen.blit(symbol_surface, (SCREEN_SIZE[0]/2-25, SCREEN_SIZE[1]/2-100))
        GameApp.screen.blit(text_surface, (SCREEN_SIZE[0]/2-65, SCREEN_SIZE[1]/2))
        GameApp.screen.blit(quit_surface, (SCREEN_SIZE[0]/2-150, SCREEN_SIZE[1]/2+50))
        GameApp.screen.blit(resume_surface, (SCREEN_SIZE[0]/2+65, SCREEN_SIZE[1]/2+50))
        pygame.display.update()

    def check_conditions(self):
        while True:
            self.time_delta = GameApp.game_clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE or event.key == K_r:
                        return "game_play"
                    elif event.key == K_q:
                        GameApp.game_state = "not_running"
                        return "main_menu"
                        
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
            GameApp.current_score += 1

class GameApp():
    current_score = None 
    screen = None 
    player_list = None 
    current_player = None 
    high_score_list = None 
    menu_system = None
    game_state = "not_running"
    game_clock = None
    gui_manager = None

    @classmethod
    def initialize(cls):
        cls.current_score = 0
        pygame.init()
        cls.screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, 32)
        cls.gui_manager = pygame_gui.UIManager(SCREEN_SIZE)
        cls.game_clock = pygame.time.Clock()
        cls.player_list = sync_player_list()
        cls.current_player = Player("default_player", 0)
        cls.high_score_list = sync_high_score_list()
        cls.menu_system = MenuStateMachine()
        cls.create_menus()
        
        #Set-up user-data files
        if not os.path.isdir("user_data"):
            os.mkdir("user_data")

        Path(HIGH_SCORE_FILE).touch()
        Path(PLAYER_DATA_FILE).touch()

    @classmethod
    def run(cls):
        cls.menu_system.process()

    @classmethod
    def create_menus(cls):
        cls.menu_system.add_state(SplashScreenMenu("splash_screen"))
        cls.menu_system.add_state(SelectPlayerMenu("select_player"))
        cls.menu_system.add_state(MainMenu("main_menu"))
        cls.menu_system.add_state(ExitConfirmMenu("exit_confirm"))
        cls.menu_system.add_state(CreatePlayerMenu("create_player"))
        cls.menu_system.add_state(AboutMenu("about"))
        cls.menu_system.add_state(GamePlayMenu("game_play"))
        cls.menu_system.add_state(GameResultMenu("game_result"))
        cls.menu_system.add_state(PauseScreenMenu("pause_screen"))
        cls.menu_system.add_state(HighScoresMenu("high_scores"))
        cls.menu_system.set_state("splash_screen")

    @classmethod
    def isHighScore(cls):
        if len(cls.high_score_list) < 10:
            return True

        if len(cls.high_score_list) > 0:
            lowest_high = cls.high_score_list[len(cls.high_score_list) - 1][1]
            if cls.current_score > lowest_high:
                return True
            else:
                return False 
        else:
            return True

    @classmethod
    def update_high_scores(cls, player):
        list_length = len(cls.high_score_list)
        if list_length == 0:
            cls.high_score_list.append([player.name, player.high_score])
        elif list_length < 10:
            for index in range(0, list_length):
                if cls.high_score_list[index][1] < player.high_score:
                    cls.high_score_list.insert(index, [player.name, player.high_score])
                    break
            else:
                cls.high_score_list.append([player.name, player.high_score])
        else:
            for index in range(0, list_length):
                if cls.high_score_list[index][1] < player.high_score:
                    cls.high_score_list.insert(index, [player.name, player.high_score])
                    break

        while len(cls.high_score_list) > 10:
            cls.high_score_list.pop()

        cls.high_score_list = sync_high_score_list(cls.high_score_list)
    
    @classmethod
    def update_player_data(cls, player):
        for pl in cls.player_list:
            if pl[0] == player.name:
                if pl[1] < player.high_score:
                    pl[1] = player.high_score

        cls.player_list = sync_player_list(cls.player_list)

if __name__ == "__main__":
    GameApp.initialize()
    GameApp.run()
