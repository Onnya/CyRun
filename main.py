import os
import sys
import pygame
from pygame.locals import *
import parallax
from image_tools import load_image

sys.path.append("../")


pygame.init()
screen = pygame.display.set_mode((700, 450), pygame.DOUBLEBUF)
size = width, height = 700, 450
orientation = 'horizontal'
fps = 350
pygame.display.set_caption('CyRun')
pygame.mouse.set_visible(0)
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
objects = pygame.sprite.Group()
clock = pygame.time.Clock()


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2 + 200)


class Floor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(objects, all_sprites)
        self.image = pygame.Surface([700, 10])
        self.image.fill("black")
        self.rect = pygame.Rect(0, 440, 700, 10)
        pygame.draw.rect(self.image, pygame.Color("black"), (0, 440, 700, 10))


class Player(pygame.sprite.Sprite):
    image = load_image("charac.png")

    def __init__(self, pos):
        super().__init__(players, all_sprites)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1] - self.rect.h

    def update(self, *args):
        global speed
        if args:
            if args[0] == "KEYDOWN" and args[1] == "RIGHT":
                speed += 1
            elif args[0] == "KEYUP" and args[1] == "RIGHT":
                speed -= 1
            elif args[0] == "KEYDOWN" and args[1] == "LEFT":
                speed -= 1
            elif args[0] == "KEYUP" and args[1] == "LEFT":
                speed += 1
        self.rect.x += speed


bg = parallax.ParallaxSurface((700, 450), pygame.RLEACCEL)
bg.add('far-buildings.png', 17)
bg.add('back-buildings.png', 9)
bg.add('foreground.png', 5)

floor = Floor()
pl = Player(floor.rect.bottomleft)
camera = Camera()


run = True
speed = 0
while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN and event.key == K_RIGHT:
            pl.update("KEYDOWN", "RIGHT")
        if event.type == KEYUP and event.key == K_RIGHT:
            pl.update("KEYUP", "RIGHT")
        if event.type == KEYDOWN and event.key == K_LEFT:
            pl.update("KEYDOWN", "LEFT")
        if event.type == KEYUP and event.key == K_LEFT:
            pl.update("KEYUP", "LEFT")
    bg.scroll(speed, orientation)
    bg.draw(screen)
    all_sprites.draw(screen)
    players.update()
    camera.update(pl)
    for sprite in all_sprites:
        camera.apply(sprite)

    pygame.display.flip()
    clock.tick(fps)