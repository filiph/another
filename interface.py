# Slideshow from http://bazaar.launchpad.net/~matio/pypicslideshow/main/view/head:/pypicslideshow.py

import os

import pygame
from pygame import *

from lib.image_renderer import ImageRenderer
from lib.manager import Manager
from lib.vote_history_manager import VoteHistoryManager
from lib.slideshow import rationalSizer, tran_none

import random

import logging
import logging.handlers

# create logger
logger = logging.getLogger("another")
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
# create file handler and set level to info
fh = logging.handlers.TimedRotatingFileHandler("interface.log", when="D", interval=1)
fh.setFormatter(formatter)
logger.addHandler(fh)

FULLSCREEN = True
RESOLUTION = (800, 600)
PATH_TO_SCRIPT = os.path.dirname(os.path.realpath(__file__))
MONKEY_TESTING = True

class Interface:
    def __init__(self, manager, renderer, fullscreen=FULLSCREEN, resolution=RESOLUTION):
        self.manager = manager
        self.renderer = renderer

        self.fullscreen = fullscreen
        self.resolution = resolution  # will be overridden if fullscreen, though

        all_images_ready = True
        for ph in self.manager.pop.phenotypes:
            started = self.renderer.start_image_render(ph)
            if started:
                all_images_ready = False

        if not all_images_ready:
            logger.info("Waiting for render of all images first.")
            self.renderer.wait_until_done()

    CHECK_INTERVAL = 1
    CHECK_USER_EVENT = pygame.USEREVENT + 1
    MONKEY_TESTING_EVENT = pygame.USEREVENT + 2

    def run(self, monkey_testing=False):
        # Initialize PyGame
        pygame.display.init()
        if self.fullscreen:
            self.resolution = pygame.display.list_modes()[0]
            self.main_surface = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        else:
            self.main_surface = pygame.display.set_mode(self.resolution)
        pygame.display.update()

        pygame.time.set_timer(self.CHECK_USER_EVENT, self.CHECK_INTERVAL * 1000)

        if monkey_testing:
            pygame.time.set_timer(self.MONKEY_TESTING_EVENT, 500)

        self.show_next()

        while True:
            for event in pygame.event.get():
                if (event.type == pygame.QUIT or
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                    self.manager.save()
                    self.manager.close()
                    self.renderer.close()
                    pygame.quit()
                    return 0
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                    self.manager.yes_to_current_phenotype()
                    self.show_next()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    self.manager.no_to_current_phenotype()
                    self.show_next()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.manager.meh_to_current_phenotype()
                    self.show_next()
                elif event.type == self.CHECK_USER_EVENT:
                    self.renderer.check_image_renders()
                    new_generation = self.manager.step()
                    if new_generation is not None:
                        for ph in new_generation:
                            self.renderer.start_image_render(ph)
                    # TODO: if idle, call Manager.parallelComputation() - creates 'Australia'
                    #       phenotypes that can be shown and voted for.
                elif event.type == self.MONKEY_TESTING_EVENT:
                    key = random.choice([pygame.K_y, pygame.K_n])
                    try:
                        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': key}))
                    except pygame.error as e:
                        logger.error("Monkey testing error: %s", e)

            pygame.time.wait(20)  # let the processor chill for a bit

    def show_phenotype_image(self, ph):
        logger.debug("Showing phenotype %s.", ph)
        blitdata = rationalSizer(pygame.image.load(self.renderer.get_image_path(ph)),
                                 self.resolution)
        self.main_surface = tran_none(self.main_surface, blitdata)

    def show_next(self):
        ph = self.manager.get_next_phenotype(self.renderer.check_image_available)
        self.show_phenotype_image(ph)

if __name__ == '__main__':
    manager = Manager(size=5, min_votes=5, directory=os.getcwd(), vote_history=VoteHistoryManager())
    try:
        manager.load()
    except IOError:
        manager.create_from_scratch()
    renderer = ImageRenderer(os.path.join(os.getcwd(), "images"))

    interface = Interface(manager, renderer)
    interface.run(monkey_testing=MONKEY_TESTING)
