import os
import sys
import random
import pygame
from pygame.locals import *
import pyparallax as parallax
from image_tools import load_image
from lvl_tools import gen_lvl
import json


pygame.init()
screen = pygame.display.set_mode((700, 450), pygame.DOUBLEBUF)
pygame.display.set_icon(load_image('logo.png'))
size = width, height = 700, 450
orientation = 'horizontal'
fps = 450
pygame.display.set_caption('CyRun')
pygame.mixer.music.load(os.path.join('data', "main.ogg"))
pygame.mixer.music.play(0)
pygame.mixer.music.set_volume(0.01)
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
objects = pygame.sprite.Group()
borders = pygame.sprite.Group()
enemies = pygame.sprite.Group()
visions = pygame.sprite.Group()
bullets = pygame.sprite.Group()
non_col_objects = pygame.sprite.Group()
hud_group = pygame.sprite.Group()
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
    if pl.health > 0:
        save = {
            "health": pl.health,
            "score": pl.score
        }
        with open(os.path.join("data", "load_game.json"), mode="w") as text:
            json.dump(save, text)
    pygame.quit()
    sys.exit()


def start_screen():
    pygame.mouse.set_visible(1)

    img = load_image('dmaintheme.png')
    screen.blit(img, (0, 0))

    img = load_image('text.png')
    screen.blit(img, (100, 30))

    img = load_image('cont.png')
    screen.blit(img, (230, 230))

    img = load_image('ng.png')
    screen.blit(img, (230, 275))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                x = event.pos[0]
                y = event.pos[1]
                if (230 <= x <= 430) and (275 <= y <= 310):
                    new_game()
                    return
                elif (230 <= x <= 430) and (230 <= y <= 265):
                    continue_game()
                    return
        pygame.display.flip()


def continue_game():
    with open(os.path.join("data", "load_game.json")) as text:
        objs = json.load(text)
    new_game(health=objs["health"], score=objs["score"])


def load_lvl(new=False):
    global objects, enemies, visions, bullets, non_col_objects
    lvl = gen_lvl()
    pl.reset()
    if new:
        pl.speed += 1
    camera.reset()
    fl.reset()
    vb.reset()
    hb.reset()
    nb.reset()
    objects = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    visions = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    non_col_objects = pygame.sprite.Group()

    Object("next_lvl.png", -1, None, 1550, 150)

    with open(os.path.join('data', "params.json")) as json_file:
        params = json.load(json_file)

    chests = 3
    barrels = 4

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

                if round(random.random()) and (barrels > 0):
                    barrels -= 1
                    bar = random.choice(("bbar", "rbar", "ybar"))
                    x = random.randint(x, x + p.rec_params()[0] - 24)
                    Object(params[bar]["name"], None, None, x, y - 40, group=True)
                else:
                    chance = random.randint(-1, 10 - i)
                    if chance == 0 and chests > 0:
                        chests -= 1
                        x = random.randint(x, x + p.rec_params()[0] - 30)
                        y -= 30
                        ch = random.choice(("bcch", "gcch", "rcch", "wcch"))
                        if ch == "rcch":
                            Chest(params[ch]["name"], "health", x, y)
                        elif ch == "gcch":
                            Chest(params[ch]["name"], "score", x, y)
                        elif ch == "wcch":
                            Chest(params[ch]["name"], "ammo", x, y)
                        else:
                            Chest(params[ch]["name"], "gun", x, y)

    for i in range(5):
        Enemy()


def hud():
    img = load_image('health.png')
    screen.blit(img, (20, 20))

    h = str(round(pl.health)).rjust(2, "0")
    n1.update(int(h[0]))
    n2.update(int(h[1]))

    s = str(round(pl.score)).rjust(5, "0")[-5:]
    s1.update(int(s[0]))
    s2.update(int(s[1]))
    s3.update(int(s[2]))
    s4.update(int(s[3]))
    s5.update(int(s[4]))

    hud_group.draw(screen)


def new_game(health=50, score=0):
    pl.health = health
    pl.score = score
    hud()


    load_lvl()

    enemy_step = 0
    pygame.mouse.set_visible(0)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
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
            if event.type == KEYDOWN and event.key == K_e:
                for i in non_col_objects:
                    if type(i) is Chest:
                        i.update(pl, op=True)

        players.update()

        if enemy_step == 0:
            enemies.update()

        bullets.update()
        non_col_objects.update(pl)

        enemy_step += 1
        enemy_step %= 4

        if not pl.hor_col:
            bg.scroll(pl.speed, orientation)

        pl.hor_col = False
        pl.ver_col = False
        pl.pl_state = False

        for sprite in enemies:
            sprite.hor_col = False
            sprite.pl_state = False

        bg.draw(screen)
        objects.draw(screen)
        enemies.draw(screen)
        visions.draw(screen)
        bullets.draw(screen)
        non_col_objects.draw(screen)

        hud()

        all_sprites.draw(screen)
        for sprite in all_sprites:
            camera.apply(sprite)
        for sprite in objects:
            camera.apply(sprite)
        for sprite in enemies:
            camera.apply(sprite)
        for sprite in visions:
            camera.apply(sprite)
        for sprite in bullets:
            camera.apply(sprite)
        for sprite in non_col_objects:
            camera.apply(sprite)
        camera.update(pl)

        if not pygame.mixer.music.get_busy():
            m = random.choice(("", "2", "3", "4"))
            pygame.mixer.music.load(os.path.join('data', f"main{m}.ogg"))
            pygame.mixer.music.play(0)
            pygame.mixer.music.set_volume(0.01)


        pygame.display.flip()
        clock.tick(fps)


class Camera:
    def __init__(self):
        self.dx = 0

    def apply(self, obj):
        obj.rect.x += self.dx

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2 + 200)

    def reset(self):
        self.dx = 0


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, group, sheet, columns, rows, x, y):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Object(pygame.sprite.Sprite):
    def __init__(self, name, colorkey, collision, x, y, group=False):
        if group:
            super().__init__(non_col_objects)
        else:
            super().__init__(objects)
        self.name = name
        image = load_image(name, color_key=colorkey)
        self.image = image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.collision = True if collision is not None else False

    def rec_params(self):
        return (self.rect.w, self.rect.h)

    def update(self, obj):
        if pygame.sprite.collide_mask(self, obj) and self.collision:
            obj.rect.x -= obj.speed
            if pygame.sprite.collide_mask(self, obj):
                obj.rect.x += obj.speed
                obj.rect.y += 1
                if pygame.sprite.collide_mask(self, obj):
                    obj.rect.y -= 2
                    obj.pl_state = True
                else:
                    obj.jump = 0
                    obj.ver_col = True
            else:
                obj.hor_col = True


class Floor(Object):
    def __init__(self):
        super(Object, self).__init__(borders, all_sprites)
        self.collision = True
        self.image = pygame.Surface([1500, 10])
        self.image.fill("black")
        self.rect = pygame.Rect(0, 440, 1500, 10)
        self.mask = pygame.mask.from_surface(self.image)

    def reset(self):
        self.rect = pygame.Rect(0, 440, 1500, 10)


class Border(Object):
    def __init__(self, type):
        super(Object, self).__init__(borders, all_sprites)
        self.type = type
        self.collision = True
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

    def reset(self):
        if self.type == "v":
            self.rect = pygame.Rect(-1, 0, 1, 500)
        else:
            self.rect = pygame.Rect(0, 0, 1500, 1)


class NextLvlBorder(Border):
    def __init__(self):
        super(Object, self).__init__(borders, all_sprites)
        self.type = type
        self.collision = True
        self.image = pygame.Surface([1, 500])
        self.mask = pygame.mask.from_surface(self.image)
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = pygame.Rect(1500, 0, 1, 500)

    def update(self, obj):
        if type(obj) is not Player:
            super().update(obj)
        if pygame.sprite.collide_mask(self, pl):
            pl.score += 10
            load_lvl(True)

    def reset(self):
        self.rect = pygame.Rect(1500, 0, 1, 500)


class Chest(Object):
    def __init__(self, name, inside, x, y):
        super().__init__(name, None, None, x, y, group=True)
        self.open = False
        self.e = None
        self.inside = inside

    def update(self, obj, op=False):
        if pygame.sprite.collide_mask(self, obj) and (not self.open):
            if op:
                non_col_objects.remove(self.e)
                self.open = True
                self.rect.y -= 13
                self.image = load_image(f"{self.name[0]}_o_chest.png", -1)
                self.e = None
                if self.inside == "health":
                    pl.health += 10
                    if pl.health > 50:
                        pl.health = 50
                    h = str(round(pl.health)).rjust(2, "0")
                    n1.update(int(h[0]))
                    n2.update(int(h[1]))
                elif self.inside == "score":
                    pl.score += 30
                    hud()

            else:
                if self.e is None:
                    self.e = Object("e.png", None, None, self.rect.x + 30, self.rect.y - 20, group=True)
        else:
            if self.e:
                if self.e in non_col_objects:
                    non_col_objects.remove(self.e)
                    self.e = None


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
        self.health = 50
        self.pl_state = False
        self.hor_col = False
        self.ver_col = False
        self.score = 0

    def update(self, *args):
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
                objects.update(self)
                borders.update(self)

            if self.jump != 0:
                if self.pl_state:
                    self.rect.y -= 1
                    self.jump -= 1
                elif (not self.pl_state) and (self.jump == 150):
                    self.jump = 0
                else:
                    self.rect.y -= 2
                    self.jump -= 1

                objects.update(self)
                borders.update(self)
            self.rect.x += self.speed
            objects.update(self)
            borders.update(self)

    def reset(self):
        self.rect.x = -15
        self.rect.y = 440 - self.rect.h
        self.speed = 0
        self.jump = 0
        self.pl_state = False
        self.hor_col = False
        self.ver_col = False


class EnemyVision(pygame.sprite.Sprite):
    def __init__(self, enemy):
        super().__init__(visions)
        self.enemy = enemy
        self.image = pygame.Surface([150, 40])
        self.mask = pygame.mask.from_surface(self.image)
        self.image.set_colorkey(self.image.get_at((0, 0)))
        if self.enemy.speed == 1:
            self.rect = pygame.Rect(self.enemy.rect.x + 20, self.enemy.rect.y, 200, 40)
        else:
            if self.enemy.per_state:
                self.rect = pygame.Rect(self.enemy.rect.x + 20, self.enemy.rect.y, 200, 40)
            else:
                self.rect = pygame.Rect(self.enemy.rect.x - 120, self.enemy.rect.y, 200, 40)

    def update(self):
        if self.enemy.speed == 1 or self.enemy.per_state:
            self.rect = pygame.Rect(self.enemy.rect.x + 20, self.enemy.rect.y, 200, 40)
        else:
            self.rect = pygame.Rect(self.enemy.rect.x - 120, self.enemy.rect.y, 200, 40)


class Enemy(pygame.sprite.Sprite):
    image = load_image("alien.png", color_key=-1)

    def __init__(self):
        super().__init__(enemies)

        self.per_state = False

        self.gun = 150

        self.image = Enemy.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = random.choice((-1, 0, 1))
        if self.speed == 1:
            self.image = pygame.transform.flip(self.image, True, False)
            self.image.set_colorkey(self.image.get_at((0, 0)))
            self.mask = pygame.mask.from_surface(self.image)
        elif self.speed == 0:
            if round(random.random()):
                self.image = pygame.transform.flip(self.image, True, False)
                self.image.set_colorkey(self.image.get_at((0, 0)))
                self.mask = pygame.mask.from_surface(self.image)
                self.per_state = True

        self.pl_state = False
        self.hor_col = False

        self.rect.x = random.randint(100, 1450)
        self.rect.y = random.randint(0, 365)

        while pygame.sprite.spritecollideany(self, objects):
            self.rect.x = random.randint(100, 1450)
            self.rect.y = random.randint(0, 365)

        self.vision = EnemyVision(self)

    def update(self):
        if not self.pl_state:
            self.rect = self.rect.move(0, 1)
            objects.update(self)
            borders.update(self)

        if self.pl_state:
            self.rect.x += self.speed
            objects.update(self)
            borders.update(self)

        if self.hor_col:
            self.speed = -1 if self.speed == 1 else 1
            self.image = pygame.transform.flip(self.image, True, False)
            self.image.set_colorkey(self.image.get_at((0, 0)))
            self.mask = pygame.mask.from_surface(self.image)

            if self.speed == -1:
                self.rect.x -= 50
            else:
                self.rect.x += 50

        self.vision.update()

        if (not pygame.sprite.spritecollideany(self.vision, objects)) and\
                (pygame.sprite.collide_mask(self.vision, pl)) and (self.gun > 0):
            self.gun -= 1
            if self.speed == 1 or self.per_state:
                EnemyBullet(self.rect.x + 50, self.rect.y + 20, 1)
            else:
                EnemyBullet(self.rect.x, self.rect.y + 20, -1)


class EnemyBullet(AnimatedSprite):
    def __init__(self, x, y, direct):
        super().__init__(bullets, load_image("alien_bullet.png"), 1, 8, x, y)
        self.w = 200
        self.direct = direct
        self.step = 0

    def update(self):
        if self.step == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]

        self.step += 1
        self.step %= 16

        self.rect.x += self.direct
        self.w -= 1

        if pygame.sprite.collide_mask(self, pl):
            pl.health -= 0.1


            if pl.health < 0:
                save = {
                    "health": 50,
                    "score": 0
                }
                with open(os.path.join("data", "load_game.json"), mode="w") as text:
                    json.dump(save, text)
                start_screen()

            hud()

            bullets.remove(self)

        if self.w == 0:
            bullets.remove(self)


class Numbers(AnimatedSprite):
    def update(self, num):
        self.cur_frame = num
        self.image = self.frames[self.cur_frame]


bg = parallax.ParallaxSurface((700, 450), pygame.RLEACCEL)
bg.add(os.path.join('data', 'far-buildings.png'), 17)
bg.add(os.path.join('data', 'back-buildings.png'), 9)
bg.add(os.path.join('data', 'foreground.png'), 5)

fl = Floor()
vb = Border("v")
hb = Border("h")
nb = NextLvlBorder()
pl = Player()
camera = Camera()

n1 = Numbers(hud_group, load_image("numbers.png"), 10, 1, 60, 20)
n2 = Numbers(hud_group, load_image("numbers.png"), 10, 1, 90, 20)

s1 = Numbers(hud_group, load_image("numbers1.png"), 10, 1, 520, 20)
s2 = Numbers(hud_group, load_image("numbers1.png"), 10, 1, 550, 20)
s3 = Numbers(hud_group, load_image("numbers1.png"), 10, 1, 580, 20)
s4 = Numbers(hud_group, load_image("numbers1.png"), 10, 1, 610, 20)
s5 = Numbers(hud_group, load_image("numbers1.png"), 10, 1, 640, 20)

start_screen()
