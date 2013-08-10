# Slideshow from http://bazaar.launchpad.net/~matio/pypicslideshow/main/view/head:/pypicslideshow.py

import pygame
from pygame import *
from pygame.mixer import *
from pygame.locals import *
import os
import sys
from random import choice

imageTypes = ['.jpg', '.jpeg', '.png']
audioTypes = ['.ogg', '.mp3']

def getFilePaths(path, fileTypes, recursive=True):
    ## Returns list containing paths of files in /path/ that are of a file type in /fileTypes/,
    ##    if /recursive/ is False subdirectories are not checked.
    paths = []
    if recursive:
        for root, folders, files in os.walk(path, followlinks=True):
            for file in files:
                for fileType in fileTypes:
                    if file.endswith(fileType):
                        paths.append(os.path.join(root, file))
    else:
        for item in os.listdir(path):
            for fileType in fileTypes:
                if item.endswith(fileType):
                    paths.append(os.path.join(root, item))
    return paths

def rationalSizer(image, area):
    ## Returns /image/ resized for /area/ maintaining origional aspect ratio.
    ## Returns tuple containing x and y displacement to center resized /image/ correctly on /area/.
    # TODO: check if necessary first
    width = float(image.get_width())
    height = float(image.get_height())
    xSizer = width / area[0]
    ySizer = height / area[1]
    if xSizer >= ySizer:
        sizer = xSizer
        yDisplace = int((area[1] - height/xSizer) / 2)
        xDisplace = 0
    else:
        sizer = ySizer
        xDisplace = int((area[0] - width/ySizer) / 2)
        yDisplace = 0
    return pygame.transform.scale(image, (int(width/sizer),int(height/sizer))), (xDisplace, yDisplace)

def run(resolution=(400,300), fullscreen=True, path=os.environ['HOME']+'/Pictures/', recursive=True,
        mpath=os.environ['HOME']+'/Music/', order=False, delay=5, transition='None'):
    ## Main Function
    ## Runs a slideshow based on parameters given.
    pygame.display.init()
    if fullscreen:
        resolution = pygame.display.list_modes()[0]
        main_surface = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        main_surface = pygame.display.set_mode(resolution)
    # main_surface.blit(pygame.image.load('/usr/share/pypicslideshow/img/loadingimages.png'), (100,50))
    pygame.display.update()
    images = getFilePaths(path, imageTypes, recursive=recursive)
    if not len(images) > 0:
        print('\n####  Error: No images found. Exiting!\n')
        sys.exit(1)
    if not mpath == 'None':
        main_surface.fill((0, 0, 0))
        # main_surface.blit(pygame.image.load('/usr/share/pypicslideshow/img/loadingmusic.png'), (100,50))
        pygame.display.update()
        music = getFilePaths(mpath, audioTypes, recursive=True)
        if not len(music) > 0:
            print('\n##  Warning: No music found. Continuing without music...')
    else:
        music = []
    i = 0
    ip = -1
    musicc = 0
    delay = delay * 1000
    if not delay > 0:
        print('\n##  Warning: Delay too short. Continuing with delay of 10s...')
        delay = 10000
#     if transition not in libtrans.transitions.keys():
#         print('\n##  Warning: ' + transition + ' is not a valid transition. Continuing with no transition...')
#         transition = 'None'
    pygame.time.set_timer(pygame.USEREVENT + 1, delay) # TODO: reset timer every time user makes choice
    TRACK_END = USEREVENT + 2
    if len(music) > 0:
        pygame.mixer.init()
        if order:
            song = music[musicc]
        else:
            song = choice(music)
        print('\nPlaying:   ' + song)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(TRACK_END)


    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                return 0
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT):
                i += 1
                if i >= len(images):
                    i = 0
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT):
                i-=1
                if i <= -1:
                    i = len(images) - 1
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return 0
            elif event.type == pygame.USEREVENT + 1:
                i += 1
                if i >= len(images):
                    i = 0
            if event.type == TRACK_END:
                if order:
                    if musicc >= len(music) - 1:
                        musicc = 0
                    else:
                        musicc += 1
                    song = music[musicc]
                else:
                    song = choice(music)
                print('\nPlaying:   ' + song)
                pygame.mixer.music.load(song)
                pygame.mixer.music.play()
        if i != ip:
            print('\nShowing:   ' + images[i])
            blitdata = rationalSizer(pygame.image.load(images[i]), resolution)
            main_surface = tran_none(main_surface, blitdata)
            ip = i

def tran_none(mainSurface, blitdata):
    mainSurface.fill((0, 0, 0))
    mainSurface.blit(blitdata[0], blitdata[1])
    pygame.display.update()
    return mainSurface

if __name__ == '__main__':
    resolution = (800,600)
    fullscreen = True
    path = "/Users/filiph/dev/blender"
    recursive = True
    delay = 5
    save = False
    load = False
    fake = False
    order = False
    music = "None"
    transition = 'None'
    run(resolution, fullscreen, path, recursive, music, order, delay, transition)
