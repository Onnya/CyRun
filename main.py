import os
import sys
import pygame
from pygame.locals import *
import parallax
from image_tools import load_image
from lvl_tools import gen_lvl
import json
from pprint import pprint


pygame.init()
screen = pygame.display.set_mode((700, 450), pygame.DOUBLEBUF)
pygame.display.set_icon(load_image('logo.png'))
size = width, height = 700, 450
orientation = 'horizontal'
fps = 30
pygame.display.set_caption('CyRun')
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
objects = pygame.sprite.Group()
borders = pygame.sprite.Group()
clock = pygame.time.Clock()


def info():
    print(f'''
    speed: {pl.speed}
    jump: {pl.jump}
    ver_col: {pl.ver_col}
    hor_col: {pl.hor_col}
    pl_state: {pl.pl_state}
    ''')


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    img = load_image('dmaintheme.png')
    screen.blit(img, (0, 0))

    img = load_image('text.png')
    screen.blit(img, (100, 30))

    img = load_image('cont.png')
    screen.blit(img, (230, 230))

    img = load_image('ng.png')
    screen.blit(img, (230, 275))

    #font = pygame.font.Font(None, 30)
    #text_coord = 50
    #for line in intro_text:
    #    string_rendered = font.render(line, 1, pygame.Color('black'))
    #    intro_rect = string_rendered.get_rect()
    #    text_coord += 10
    #    intro_rect.top = text_coord
    #    intro_rect.x = 10
    #    text_coord += intro_rect.height
    #    screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                x = event.pos[0]
                y = event.pos[1]
                if (230 <= x <= 430) and (275 <= y <= 310):
                    return
        pygame.display.flip()


def load_lvl():
    global objects
    lvl = gen_lvl()

    pl.reset()
    camera.reset()
    objects = pygame.sprite.Group()

    Object("next_lvl.png", -1, None, 1550, 150)

    with open(os.path.join('data', "params.json")) as json_file:
        params = json.load(json_file)
    for i in range(len(lvl)):
        for j in range(len(lvl[i])):
            if type(lvl[i][j]) is str:
                x = 100 + sum([lvl[i][m][0] for m in range(j)])
                y = 410 - sum([lvl[m][j][1] for m in range(i)])
                n = params[lvl[i][j]]["name"]
                c = params[lvl[i][j]]["colorkey"]
                l = params[lvl[i][j]]["collision"]
                p = Object(n, c, l, x, y)
                lvl[i][j] = p.rec_params()


class Camera:
    def __init__(self):
        self.dx = 0

    def apply(self, obj):
        obj.rect.x += self.dx

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2 + 200)

    def reset(self):
        self.dx = 0


class Object(pygame.sprite.Sprite):
    def __init__(self, name, colorkey, collision, x, y):
        super().__init__(objects)
        image = load_image(name, color_key=colorkey)
        self.image = image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.collision = True if collision is not None else False

    def rec_params(self):
        return (self.rect.w, self.rect.h)

    def update(self):
        if pygame.sprite.collide_mask(self, pl):
            pl.rect.x -= pl.speed
            if pygame.sprite.collide_mask(self, pl):
                pl.rect.x += pl.speed
                pl.rect.y += 1
                if pygame.sprite.collide_mask(self, pl):
                    pl.rect.y -= 2
                    pl.pl_state = True
                else:
                    pl.jump = 0
                    pl.ver_col = True
            else:
                pl.hor_col = True


class Floor(Object):
    def __init__(self):
        super(Object, self).__init__(borders, all_sprites)
        self.image = pygame.Surface([1500, 10])
        self.image.fill("black")
        self.rect = pygame.Rect(0, 440, 1500, 10)
        self.mask = pygame.mask.from_surface(self.image)


class Border(Object):
    def __init__(self, type):
        super(Object, self).__init__(borders, all_sprites)
        self.type = type
        if type == "v":
            self.image = pygame.Surface([1, 500])
            self.mask = pygame.mask.from_surface(self.image)
            self.image.set_colorkey(self.image.get_at((0, 0)))
            self.rect = pygame.Rect(-1, 0, 1, 500)
        else:
            self.image = pygame.Surface([1500, 1])
            self.mask = pygame.mask.from_surface(self.image)
            self.image.set_colorkey(self.image.get_at((0, 0)))
            self.rect = pygame.Rect(0, 0, 1500, 1)


class Player(pygame.sprite.Sprite):
    image = load_image("charac1.png")

    def __init__(self):
        super().__init__(players, all_sprites)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = - 15
        self.rect.y = 440 - self.rect.h
        self.speed = 0
        self.jump = 0
        self.pl_state = False
        self.hor_col = False
        self.ver_col = False

    def update(self, *args):
        global objects
        if args:
            if args[0] == "KEYDOWN" and args[1] == "RIGHT":
                self.speed += 1
            elif args[0] == "KEYUP" and args[1] == "RIGHT":
                self.speed -= 1
            elif args[0] == "KEYDOWN" and args[1] == "LEFT":
                self.speed -= 1
            elif args[0] == "KEYUP" and args[1] == "LEFT":
                self.speed += 1
            elif args[0] == "KEYDOWN" and args[1] == "UP" and self.jump == 0:
                self.jump = 150
        else:
            if not self.pl_state:
                self.rect = self.rect.move(0, 1)
                objects.update()
                borders.update()
            self.rect.x += self.speed
            objects.update()
            borders.update()
            if self.jump != 0:
                if self.pl_state:
                    self.rect.y -= 1
                    self.jump -= 1
                elif (not self.pl_state) and (self.jump == 150):
                    self.jump = 0
                else:
                    self.rect.y -= 2
                    self.jump -= 1

                objects.update()
                borders.update()

    def reset(self):
        self.rect.x = - 15
        self.rect.y = 440 - self.rect.h
        self.speed = 0
        self.jump = 0
        self.pl_state = False
        self.hor_col = False
        self.ver_col = False


start_screen()

bg = parallax.ParallaxSurface((700, 450), pygame.RLEACCEL)
bg.add(os.path.join('data', 'far-buildings.png'), 17)
bg.add(os.path.join('data', 'back-buildings.png'), 9)
bg.add(os.path.join('data', 'foreground.png'), 5)

Floor()
Border("v")
Border("h")
pl = Player()
camera = Camera()

load_lvl()

run = True
pygame.mouse.set_visible(0)

while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN and event.key == K_RIGHT:
            pl.update("KEYDOWN", "RIGHT")
        if event.type == KEYUP and event.key == K_RIGHT:
            pl.update("KEYUP", "RIGHT")
            info()
        if event.type == KEYDOWN and event.key == K_LEFT:
            pl.update("KEYDOWN", "LEFT")
        if event.type == KEYUP and event.key == K_LEFT:
            pl.update("KEYUP", "LEFT")
            info()
        if event.type == KEYDOWN and event.key == K_UP:
            pl.update("KEYDOWN", "UP")
            info()

    players.update()


    if not pl.hor_col:
        bg.scroll(pl.speed, orientation)

    pl.hor_col = False
    pl.ver_col = False
    pl.pl_state = False

    bg.draw(screen)
    objects.draw(screen)
    all_sprites.draw(screen)
    for sprite in all_sprites:
        camera.apply(sprite)
    for sprite in objects:
        camera.apply(sprite)
    camera.update(pl)


    pygame.display.flip()
    clock.tick(fps)
