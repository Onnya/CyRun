import os, sys
import pygame
from pygame.locals import *
import parallax

sys.path.append("../")


pygame.init()
screen = pygame.display.set_mode((700, 450), pygame.DOUBLEBUF)
pygame.display.set_caption('CyRun')
pygame.mouse.set_visible(0)

orientation = 'horizontal'

bg = parallax.ParallaxSurface((700, 450), pygame.RLEACCEL)
bg.add('far-buildings.png', 17)
bg.add('back-buildings.png', 9)
bg.add('foreground.png', 5)

run = True
speed = 0
while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN and event.key == K_RIGHT:
            speed += 1
        if event.type == KEYUP and event.key == K_RIGHT:
            speed -= 1
        if event.type == KEYDOWN and event.key == K_LEFT:
            speed -= 1
        if event.type == KEYUP and event.key == K_LEFT:
            speed += 1

    bg.scroll(speed, orientation)
    bg.draw(screen)
    pygame.display.flip()