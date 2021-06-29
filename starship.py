import pygame
import pygame_gui
from pygame.locals import *
from abc import ABCMeta, abstractmethod
from vector2 import Vector2
from random import randint
import time
import csv
import os
from pathlib import Path
from models import Player, Score, Session

SCREEN_SIZE = (1366, 768)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPACECRAFT_SPEED = 400

INTRO_SCREEN_FILE = "images/SplashScreenImage.png"
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

class GameState(metaclass=ABCMeta):
    def __init__(self, name):
        self.name = name
        self.gui_manager = pygame_gui.UIManager(SCREEN_SIZE)
        self.time_delta = 0.0
        self.internal_clock = pygame.time.Clock()
        self.initialize_gui_elements()

    def initialize_gui_elements(self):
        pass

    def do_actions(self, backfill=True):
        self.time_delta = GameApp.game_clock.tick(120)/1000.0

        if backfill:
            GameApp.screen.fill(BLACK)
        else:
            if GameApp.old_screen:
                GameApp.screen.blit(GameApp.old_screen, (0,0))
            darkening = pygame.Surface((1366, 768))
            darkening.set_alpha(190)
            darkening.fill((0, 0, 0))
            GameApp.screen.blit(darkening, (0,0))

        self.gui_manager.update(self.time_delta)
        self.gui_manager.draw_ui(GameApp.screen)
        pygame.display.update()
        
    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass
        
class SplashScreenMenu(GameState):
    def do_actions(self):
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
    def initialize_gui_elements(self):
        pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((384, 100), (600, 40)), text="SELECT A PLAYER", manager=self.gui_manager)
        pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((384, 150), (600, 40)), text="TO CREATE A NEW PLAYER PRESS 'C'", manager=self.gui_manager)
        pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((384, 200), (600, 40)), text="TO DELETE A PLAYER PRESS 'X'", manager=self.gui_manager)

        my_list = []
        for player in GameApp.get_player_list():
            my_list.append(player[0])
                    
        self.selection_list = pygame_gui.elements.ui_selection_list.UISelectionList(relative_rect= pygame.Rect((384,250), (600,300)), item_list= my_list, manager= self.gui_manager)

        self.delete_player_button = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((384, 550), (175, 40)), text="DELETE", manager=self.gui_manager)
        self.create_player_button = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((598, 550), (175, 40)), text="CREATE NEW", manager=self.gui_manager)
        self.continue_button = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((810, 550), (174, 40)), text="CONTINUE", manager=self.gui_manager)

    def refresh_gui_elements(self):
        my_list = []
        for player in GameApp.get_player_list():
            my_list.append(player[0])

        self.selection_list.set_item_list(my_list)

    def do_actions(self):
        if self.selection_list.get_single_selection() == None:
            self.delete_player_button.disable()
            self.continue_button.disable()
        else:
            self.delete_player_button.enable()
            self.continue_button.enable()
    
        super().do_actions()

    def check_conditions(self):
        for event in pygame.event.get():
            self.gui_manager.process_events(event)
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    GameApp.current_player = GameApp.session.query(Player).filter_by(name=self.selection_list.get_single_selection()).first()
                    if not GameApp.current_player:
                        return None
                    else:
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
                        GameApp.player_buff = GameApp.session.query(Player).filter_by(name=self.selection_list.get_single_selection()).first()
                        if GameApp.player_buff:
                            self.confirm_dialog = pygame_gui.windows.ui_confirmation_dialog.UIConfirmationDialog(rect=pygame.Rect((503,259), (360, 250)), manager=self.gui_manager, window_title="DELETE PLAYER!", action_short_name="Delete", action_long_desc="Are you sure you want to delete '" + GameApp.player_buff.name + "'? This cannot be undone!", blocking=True)
                        return None

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.continue_button:
                        GameApp.current_player = GameApp.session.query(Player).filter_by(name=self.selection_list.get_single_selection()).first()
                        return "main_menu"
                    elif event.ui_element == self.delete_player_button:
                        if len(GameApp.player_list) > 0:
                            GameApp.player_buff = GameApp.session.query(Player).filter_by(name=self.selection_list.get_single_selection()).first()
                            if GameApp.player_buff:
                                self.confirm_dialog = pygame_gui.windows.ui_confirmation_dialog.UIConfirmationDialog(rect=pygame.Rect((503,259), (360, 250)), manager=self.gui_manager, window_title="Delete", action_short_name="Delete", action_long_desc="Are you sure you want to Delete this player? This cannot be undone!", blocking=True)
                        return None
                    elif event.ui_element == self.create_player_button:
                        return "create_player"
                elif event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    if event.ui_element == self.confirm_dialog:
                        GameApp.session.delete(GameApp.player_buff)
                        GameApp.refresh_high_scores()
                        self.refresh_gui_elements()
                        return None

    def entry_actions(self):
        GameApp.player_list = GameApp.get_player_list()
        self.refresh_gui_elements()

class CreatePlayerMenu(GameState):
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

        super().do_actions()
        
    def check_conditions(self):
        for event in pygame.event.get():
            self.gui_manager.process_events(event)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "select_player"
                elif event.key == K_RETURN:
                    inp = self.text_box.get_text()
                    if len(inp) > 0:
                        new_player = Player(name=inp)
                        GameApp.session.add(new_player)
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
                            new_player = Player(name=inp)
                            GameApp.session.add(new_player)
                            return "select_player"
                        else:
                            return None

    def entry_actions(self):
        self.text_box.set_text("")

    def exit_actions(self):
        pass

class MainMenu(GameState):
    def initialize_gui_elements(self):
        self.new_game_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 160), (600, 40)), text="Start Game", manager=self.gui_manager)
        self.change_plyr_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 210), (600, 40)), text="Change Current Player", manager=self.gui_manager)
        self.hi_scores_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 260), (600, 40)), text="High Scores", manager=self.gui_manager)
        self.about_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 310), (600, 40)), text="About This Game", manager=self.gui_manager)
        self.exit_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 360), (600, 40)), text="Quit Game", manager=self.gui_manager)

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
                    self.confirm_dialog = pygame_gui.windows.ui_confirmation_dialog.UIConfirmationDialog(rect=pygame.Rect((503,259), (360, 250)), manager=self.gui_manager, window_title="QUIT GAME", action_short_name="Quit", action_long_desc="Are you sure you want to quit the game?", blocking=True)
                    return None
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
                        self.confirm_dialog = pygame_gui.windows.ui_confirmation_dialog.UIConfirmationDialog(rect=pygame.Rect((503,259), (360, 250)), manager=self.gui_manager, window_title="QUIT GAME", action_short_name="Quit", action_long_desc="Are you sure you want to quit the game?", blocking=True)
                        return None
                elif event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    if event.ui_element == self.confirm_dialog:
                        pygame.quit()
                        exit()

class HighScoresMenu(GameState):
    def initialize_gui_elements(self):
        self.build_scores_table()
        self.title_label = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((383, 160), (600, 40)), text="HIGH SCORES", manager=self.gui_manager)
        self.back_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 470), (175, 40)), text="BACK", manager=self.gui_manager)
        self.build_scores_table()

    def do_actions(self):
        self.time_delta = self.internal_clock.tick(60)/1000.0
        GameApp.screen.fill(BLACK)
        self.gui_manager.update(self.time_delta)
        self.gui_manager.draw_ui(GameApp.screen)
        pygame.display.update()

    def build_scores_table(self):
        counter = 1
        self.score_string = ""
        self.score_string += "{:2}  {:64} {}<br>".format("","<u><b>PLAYER</b></u>", "<u><b>SCORE</b></u>")
        for score in GameApp.high_score_list:
            self.score_string += "{:>2}. {:50} {}<br>".format(str(counter), score[0], str(score[1]))
            counter += 1

        self.high_scores_list = pygame_gui.elements.UITextBox(html_text=self.score_string, relative_rect=pygame.Rect((383,220), (600, 230)), manager=self.gui_manager)

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

    def entry_actions(self):
        self.build_scores_table()

class AboutMenu(GameState):
    def initialize_gui_elements(self):
        self.title_label = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((383, 160), (600, 40)), text="ABOUT STARSHIP ODYSSEY", manager=self.gui_manager)
        about_file = open(ABOUT_FILE, "r", 1)
        string = ""
        for line in about_file:
            string += string.join(str(line))

        string = string.rstrip(string[-1])
        about_file.close()
            
        self.about_text = pygame_gui.elements.ui_text_box.UITextBox(relative_rect=pygame.Rect((383, 210), (600, 300)), manager=self.gui_manager, html_text=string)
        self.back_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((383, 550), (175, 40)), text="BACK", manager=self.gui_manager)

    def check_conditions(self):
        for event in pygame.event.get():
            self.gui_manager.process_events(event)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "main_menu"
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.back_btn:
                        return "main_menu"

class GamePlayMenu(GameState):
    def __init__(self, name):
        super().__init__(name)
        self.reset_game()
        self.number_font = pygame.font.Font("freesansbold.ttf", 96)

    def initialize_gui_elements(self):
        pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((20, 20), (150, 40)), text="PLAYER:", manager=self.gui_manager)
        self.name_pane = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((20, 70), (150, 40)), text=GameApp.current_player.name , manager=self.gui_manager)
        pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((20, 120), (150, 40)), text="PERSONAL BEST:", manager=self.gui_manager)
        self.pb_pane = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((20, 180), (150, 40)), text=str(GameApp.current_player.personal_best), manager=self.gui_manager)
        self.score_pane = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((608, 20), (150, 40)), text="SCORE: " + str(GameApp.current_score), manager=self.gui_manager)

    def reset_game(self):
        GameApp.current_score = 0
        self.game_objects = []
        starship = Starship(self, (SCREEN_SIZE[0]/2.0), (SCREEN_SIZE[1]-100))
        self.starship = starship
        self.game_objects.append(starship)

        for _ in range(10):
            meteor_speed = randint(800, 1000) * 1.0
            x_location = randint(0, SCREEN_SIZE[0])
            meteor = Meteor(self, x_location, -20, meteor_speed)
            self.game_objects.append(meteor)

        self.clock = pygame.time.Clock()

    def do_actions(self):
        #super().do_actions()
        #Draw all game artifacts here
        GameApp.screen.fill(BLACK)
        for asset in self.game_objects:
            asset.render(GameApp.screen)

        self.display_score()
        #self.display_player_stats()
        self.gui_manager.update(self.time_delta)
        self.gui_manager.draw_ui(GameApp.screen)
        pygame.display.update()

        pygame.display.update()

    def display_score(self):
        self.score_pane.set_text("SCORE: " + str(GameApp.current_score))
        #score_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        #score_surface = score_font.render("SCORE:" + str(GameApp.current_score), True, WHITE, BLACK)
        #GameApp.screen.blit(score_surface, (0, 0))

    def display_player_stats(self):
        player_font = pygame.font.SysFont("inconsolata", 32, bold=True)
        player_surface = player_font.render("PLAYER: " + str(GameApp.current_player.name) + " HIGH SCORE: " + str(GameApp.current_player.personal_best), True, WHITE, BLACK)
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
        self.name_pane.set_text(GameApp.current_player.name)
        self.pb_pane.set_text(str(GameApp.current_player.personal_best))
        pygame.mouse.set_visible(False)
        
        if GameApp.game_state == "not_running":
            self.reset_game()
            GameApp.game_state = "running"
            self.count_down()
            #Start clock
        elif GameApp.game_state == "paused":
            #Reset clocking
            self.count_down()
            self.clock.tick()

        pygame.event.clear()

    def count_down(self):
        #Show countdown timer to allow player to start game comfortably 
        count = 3
        while count:
            self.do_actions()
            number_surface = self.number_font.render(str(count), True, pygame.Color("#FFFFFF"))
            number_rectangle = number_surface.get_rect()
            number_rectangle.center = ((1366/2),(768/2))
            GameApp.screen.blit(number_surface, number_rectangle)
            pygame.display.update()
            time.sleep(1)
            count -= 1

        self.do_actions()
        number_surface = self.number_font.render("GO!", True, pygame.Color("#FFFFFF"))
        number_rectangle = number_surface.get_rect()
        number_rectangle.center = ((1366/2),(768/2))
        GameApp.screen.blit(number_surface, number_rectangle)
        pygame.display.update()
        time.sleep(0.5)

    def exit_actions(self):
        pygame.mouse.set_visible(True)
        GameApp.old_screen = GameApp.screen.copy()
        
class GameResultMenu(GameState):
    def __init__(self, name):
        super().__init__(name)
        
    def initialize_gui_elements(self):
        self.menu_title = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((383, 160), (600, 40)), manager=self.gui_manager, text="GAME OVER")
        self.score_label = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((383, 250), (600, 40)), manager=self.gui_manager, text="Your score:")
        self.continue_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((808, 350), (175, 40)), text="Continue", manager=self.gui_manager)

    def do_actions(self):
        super().do_actions(False)
       
    def check_conditions(self):
        for event in pygame.event.get():
            self.gui_manager.process_events(event)
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return "main_menu"
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.continue_btn:
                        return "main_menu"

    def entry_actions(self):
        self.score_label.set_text("Your score: " + str(GameApp.current_score))
        new_score = Score(score=GameApp.current_score, player_id=GameApp.current_player.id)
        GameApp.session.add(new_score)
        GameApp.session.commit()
        
        #Check if the game result is a high-score
        if GameApp.current_score > (GameApp.high_score_list[len(GameApp.high_score_list)-1][1] if GameApp.high_score_list else 0):
            self.menu_title.set_text("CONGRATULATIONS: HIGH SCORE!")
        else:
            self.menu_title.set_text("GAME OVER!")
            
    def exit_actions(self):
        GameApp.old_screen = None
        if GameApp.current_score > GameApp.current_player.personal_best:
            #Adjust the current player's personal best
            GameApp.current_player.personal_best = GameApp.current_score
            GameApp.session.add(GameApp.current_player)

            #Refresh Current Player
            GameApp.current_player = GameApp.session.query(Player).get(GameApp.current_player.id)

        #Refresh the High-Score List
        GameApp.high_score_list = []
        high_scores = GameApp.session.query(Score).order_by(Score.score.desc()).limit(10).all()

        for score in high_scores:
            GameApp.high_score_list.append((score.player.name, score.score))

class PauseScreenMenu(GameState):
    def initialize_gui_elements(self):
        self.menu_title = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((383, 160), (600, 40)), text="GAME PAUSED", manager=self.gui_manager)
        self.question_label = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((383, 250), (600, 40)), text="What do you want to do?", manager=self.gui_manager)
        self.quit_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((480, 350), (175, 40)), text="Resign", manager=self.gui_manager)
        self.resume_btn = pygame_gui.elements.ui_button.UIButton(relative_rect=pygame.Rect((700, 350), (175, 40)), text="Resume Game", manager=self.gui_manager)

    def do_actions(self):
        super().do_actions(False)
        
    def check_conditions(self):
        for event in pygame.event.get():
            self.gui_manager.process_events(event)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_r:
                    return "game_play"
                elif event.key == K_q:
                    GameApp.game_state = "not_running"
                    return "main_menu"
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.resume_btn:
                        return "game_play"
                    elif event.ui_element == self.quit_btn:
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
        self.rect.center = (self.location.x, self.location.y)
        #self.rect.center = ((self.location.x + self.image_w/2), (self.location.y + self.image_h/2))
        #self.rect = self.image.get_rect(center=(self.location.x, self.location.y))

    def load_image(self, filename):
        self.image = pygame.image.load(filename).convert_alpha()
        self.image_w, self.image_h = self.image.get_size()
        self.rect = pygame.Rect((self.location.x-(self.image_w/2)), (self.location.y-(self.image_h/2)), self.image_w*0.70, self.image_h*0.40)
        #self.rect = self.image.get_rect(center=(self.location.x, self.location.y))

class Starship(GameAsset):
    def __init__(self, world, x_location, y_location):
        super().__init__(world, x_location, y_location)
        self.heading = Vector2(0.0, 0.0)
        self.load_image("images/space_craft.png")
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
    high_score_list = []
    menu_system = None
    game_state = "not_running"
    game_clock = None
    gui_manager = None
    session = None
    player_buff = None

    @classmethod
    def initialize(cls):
        cls.session = Session()
        cls.current_score = 0
        pygame.init()
        cls.screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, 32)
        cls.gui_manager = pygame_gui.UIManager(SCREEN_SIZE)
        cls.game_clock = pygame.time.Clock()
        cls.player_list = cls.get_player_list()
        cls.current_player = Player(name="default_player")
        cls.menu_system = MenuStateMachine()
        cls.refresh_high_scores()
        cls.create_menus()

    @classmethod
    def run(cls):
        cls.menu_system.process()

    @classmethod
    def create_menus(cls):
        cls.menu_system.add_state(AboutMenu("about"))
        cls.menu_system.add_state(CreatePlayerMenu("create_player"))
        cls.menu_system.add_state(GamePlayMenu("game_play"))
        cls.menu_system.add_state(GameResultMenu("game_result"))
        cls.menu_system.add_state(HighScoresMenu("high_scores"))
        cls.menu_system.add_state(MainMenu("main_menu"))
        cls.menu_system.add_state(PauseScreenMenu("pause_screen"))
        cls.menu_system.add_state(SelectPlayerMenu("select_player"))
        cls.menu_system.add_state(SplashScreenMenu("splash_screen"))
        cls.menu_system.set_state("splash_screen")

    @classmethod
    def isHighScore(cls):
        if GameApp.current_score > GameApp.high_score_list[9][1]:
            return True
        else:
            return False

    @classmethod
    def dep_isHighScore(cls):
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
    def add_new_player(cls, player_name):
        new_player = Player(name="player_name")
        cls.session.add(new_player)

    @classmethod
    def delete_player(cls, player_name):
        player = cls.session.query(Player).filter_by(name=player_name).first()
        cls.session.delete(player)

    @classmethod
    def get_player_list(cls):
        player_list = []
        players = cls.session.query(Player).all()
        for player in players:
            player_list.append((player.name, player.personal_best)) 

        return player_list

    @classmethod
    def refresh_high_scores(cls):
        cls.high_score_list = []
        scores = cls.session.query(Score).order_by(Score.score.desc()).limit(10).all()

        for score in scores:
            cls.high_score_list.append((score.player.name, score.score))

if __name__ == "__main__":
    GameApp.initialize()
    GameApp.run()
