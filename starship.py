import pygame
from pygame.locals import *
from vector2 import Vector2

SCREEN_SIZE = (640, 480)
BLACK = (0, 0, 0)
SPACECRAFT_SPEED = 400

class World():
    def __init__(self, surface):
        self.world_objects = []
        self.screen = surface

    def add_object(self, asset):
        self.world_objects.append(asset)

    def update(self, time_passed):
        for asset in self.world_objects:
            asset.update(time_passed)

    def render(self):
        for asset in self.world_objects:
            asset.render(self.screen)

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
        self.image = pygame.image.load("starship.png").convert_alpha()
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

def exit_procedure():
    pygame.quit()
    exit()

def main():
    pygame.init()

    display_surface = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, 32)
    pygame.display.set_caption("Starship Odyssey")
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    space_craft = Starship((SCREEN_SIZE[0]/2.0), (SCREEN_SIZE[1]-100))
    world = World(display_surface)
    world.add_object(space_craft)
    
    while True:
        for event in pygame.event.get():        
            if event.type == pygame.QUIT:
                exit_procedure()
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    exit_procedure()

        display_surface.fill(BLACK)
        time_passed = clock.tick()/1000.0
        world.update(time_passed)
        world.render()
        pygame.display.update()

if __name__ == "__main__":
    main()
