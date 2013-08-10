# Slideshow from http://bazaar.launchpad.net/~matio/pypicslideshow/main/view/head:/pypicslideshow.py

import pygame
from pygame import *
from pygame.locals import *
import os
import sys
from random import choice
import pickle
import subprocess
import time

from slideshow import getFilePaths, rationalSizer, tran_none, imageTypes

from population import *

RESOLUTION = (800, 600)
PATH_TO_SCRIPT = os.path.dirname(os.path.realpath(__file__))
PATH_TO_POP_DUMP = PATH_TO_SCRIPT + "/population.dump"
PATH_TO_RENDER_SH = PATH_TO_SCRIPT + "/dnarender.sh"

GENERATION_SIZE = 5

def load_pop_from_file():
    try:
        with open(PATH_TO_POP_DUMP, "rb") as f:
            pop = pickle.load(f)
            print("Population loaded from " + PATH_TO_POP_DUMP)
    except IOError:
        print("Population file not found. Creating first generation.")
        pop = Population()
        pop.create_first_generation(GENERATION_SIZE)
        for ph in pop.phenotypes:
            start_image_render(ph)
        while check_image_renders() > 0:
            print("Waiting for render of first batch to end")
            time.sleep(1)
    return pop


RENDER_TIMEOUT = 60
MAX_PARALLEL_RENDERS = 2
running_procs = []
render_backlog = []

def start_image_render(ph):
    if check_image_available(ph):
        return
    if check_image_renders() <= MAX_PARALLEL_RENDERS:
        try:
            FNULL = open(os.devnull, 'w')
            # TODO: set render resolution according to fullscreen resolution
            proc = subprocess.Popen([PATH_TO_RENDER_SH, ph.get_binary_string(), get_phenotype_image_path(ph)],
                    stdout=FNULL)
                    #stderr=subprocess.PIPE
            running_procs.append(proc)
        except OSError as e:
            print(str(e))
            raise
    else:
        render_backlog.append(ph)

def check_image_renders():
    """ Checks the status of background image renders. Returns number of running processes. """
    count = 0
    for proc in running_procs:
        retcode = proc.poll()
        if retcode is not None:  # process finished
            running_procs.remove(proc)
            if retcode != 0:
                print("ERROR: Render process failed")
                print(proc.stderr)
                # TODO: do something about it
            if render_backlog:
                start_image_render(render_backlog.pop(0))
        else:  # process still running
            count += 1
    return count


def save_pop_to_file(pop):
    print("Trying to save population...")
    try:
        with open(PATH_TO_POP_DUMP, "wb") as f:
            pickle.dump(pop, f)
            print("Population saved to " + PATH_TO_POP_DUMP)
    except IOError:
        print("ERROR: Couldn't write population to file.")
        raise

def get_phenotype_image_path(ph):
    # TODO: better
    return PATH_TO_SCRIPT + "/generation" + str(ph.generation) + "/" + ph.get_binary_string() + ".jpg"

def check_image_available(ph):
    # TODO: check against a list (cached)
    return os.path.isfile(get_phenotype_image_path(ph))


## START HERE ##
def run(resolution=RESOLUTION, fullscreen=True, path=PATH_TO_SCRIPT,
        recursive=True, order=False, delay=5):
    # Initialize the population
    pop = load_pop_from_file()

    ## Initialize PyGame
    pygame.display.init()
    if fullscreen:
        resolution = pygame.display.list_modes()[0]
        main_surface = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        main_surface = pygame.display.set_mode(resolution)
    pygame.display.update()
    # images = getFilePaths(path, imageTypes, recursive=recursive)
    # if not len(images) > 0:
    #     print('\n####  Error: No images found. Exiting!\n')
    #     sys.exit(1)
    #     # TODO: don't exit - create images instead
    # i = 0
    # ip = -1
    # delay = delay * 1000
    # if not delay > 0:
    #     print('\n##  Warning: Delay too short. Continuing with delay of 10s...')
    #     delay = 10000
    # pygame.time.set_timer(pygame.USEREVENT + 1, delay) # TODO: reset timer every time user makes choice
    show_phenotype_image(pop.current, resolution, main_surface)

    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                save_pop_to_file(pop)
                pygame.quit()
                return 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                pop.current.yes += 1
                ph = pop.get_next(check_image_available)
                show_phenotype_image(ph, resolution, main_surface)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                pop.current.no += 1
                ph = pop.get_next(check_image_available)
                show_phenotype_image(ph, resolution, main_surface)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pop.current.meh += 1
                ph = pop.get_next(check_image_available)
                show_phenotype_image(ph, resolution, main_surface)

            # elif event.type == pygame.USEREVENT + 1:
            #     i += 1
            #     if i >= len(images):
            #         i = 0
            #     save_pop_to_file()

def show_phenotype_image(ph, resolution, main_surface): # TODO: make into class
    print("Showing phenotype " + ph.get_binary_string())
    blitdata = rationalSizer(pygame.image.load(get_phenotype_image_path(ph)), resolution)
    main_surface = tran_none(main_surface, blitdata)

if __name__ == '__main__':
    run()
