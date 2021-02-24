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
fps = 450
pygame.display.set_caption('CyRun')
pygame.mouse.set_visible(0)
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
objects = pygame.sprite.Group()
borders = pygame.sprite.Group()
clock = pygame.time.Clock()


class Camera:
    def __init__(self):
        self.dx = 0

    def apply(self, obj):
        obj.rect.x += self.dx

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2 + 200)


class Floor(pygame.sprite.Sprite):
    def __init__(self, length):
        super().__init__(objects, all_sprites)
        self.image = pygame.Surface([length, 10])
        self.image.fill("black")
        self.rect = pygame.Rect(0, 440, length, 10)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        if pygame.sprite.collide_mask(self, pl):
            pl.pl_state = True
        else:
            pl.pl_state = False


class Border(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(borders, all_sprites)
        self.image = pygame.Surface([1, 500])
        self.mask = pygame.mask.from_surface(self.image)
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = pygame.Rect(0, 0, 1, 500)

    def update(self):
        if pygame.sprite.collide_mask(self, pl):
            pl.rect.x -= pl.speed
            pl.speed = 0


class Player(pygame.sprite.Sprite):
    image = load_image("charac1.png")

    def __init__(self, pos):
        super().__init__(players, all_sprites)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0] - 15
        self.rect.y = pos[1] - self.rect.h - 10
        self.speed = 0
        self.jump = 0
        self.pl_state = False

    def update(self, *args):
        if not pl.pl_state:
            self.rect = self.rect.move(0, 1)
        if args:
            if args[0] == "KEYDOWN" and args[1] == "RIGHT":
                pl.speed += 1
            elif args[0] == "KEYUP" and args[1] == "RIGHT":
                if pl.speed != 0:
                    pl.speed -= 1
            elif args[0] == "KEYDOWN" and args[1] == "LEFT":
                pl.speed -= 1
            elif args[0] == "KEYUP" and args[1] == "LEFT":
                if pl.speed != 0:
                    pl.speed += 1
            elif args[0] == "KEYDOWN" and args[1] == "UP" and pl.pl_state:
                pl.jump = 150
        self.rect.x += pl.speed
        if pl.jump != 0:
            self.rect.y -= 2
            pl.jump -= 1


bg = parallax.ParallaxSurface((700, 450), pygame.RLEACCEL)
bg.add('far-buildings.png', 17)
bg.add('back-buildings.png', 9)
bg.add('foreground.png', 5)

floor = Floor(1500)
lb = Border()
pl = Player(floor.rect.bottomleft)
camera = Camera()


run = True


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
        if event.type == KEYDOWN and event.key == K_UP:
            pl.update("KEYDOWN", "UP")
    borders.update()
    objects.update()
    players.update()

    bg.scroll(pl.speed, orientation)
    bg.draw(screen)
    all_sprites.draw(screen)
    for sprite in all_sprites:
        camera.apply(sprite)
    camera.update(pl)
    pygame.display.flip()
    clock.tick(fps)
