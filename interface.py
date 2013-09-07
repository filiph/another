# Slideshow from http://bazaar.launchpad.net/~matio/pypicslideshow/main/view/head:/pypicslideshow.py

import os

import pygame
from pygame import *

from lib.image_renderer import ImageRenderer
from lib.manager import Manager
from lib.slideshow import rationalSizer, tran_none


FULLSCREEN = False
RESOLUTION = (800, 600)
PATH_TO_SCRIPT = os.path.dirname(os.path.realpath(__file__))

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
            print("Waiting for render of all images first.")
            self.renderer.wait_until_done()

    CHECK_INTERVAL = 1
    CHECK_USER_EVENT = pygame.USEREVENT + 1

    def run(self):
        # Initialize PyGame
        pygame.display.init()
        if self.fullscreen:
            self.resolution = pygame.display.list_modes()[0]
            self.main_surface = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        else:
            self.main_surface = pygame.display.set_mode(self.resolution)
        pygame.display.update()

        pygame.time.set_timer(self.CHECK_USER_EVENT, self.CHECK_INTERVAL * 1000)

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
                    #TODO: save votes via manager
                    self.manager.current_phenotype.yes += 1
                    self.show_next()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    self.manager.current_phenotype.no += 1
                    self.show_next()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.manager.current_phenotype.meh += 1
                    self.show_next()
                elif event.type == self.CHECK_USER_EVENT:
                    self.renderer.check_image_renders()
                    new_generation = self.manager.step()
                    if new_generation is not None:
                        for ph in new_generation:
                            self.renderer.start_image_render(ph)
                    # TODO: if idle, call Manager.parallelComputation() - creates 'Australia'
                    #       phenotypes that can be shown and voted for.

            pygame.time.wait(20)  # let the processor chill for a bit

    def show_phenotype_image(self, ph):
        print("Showing phenotype {}".format(ph))
        blitdata = rationalSizer(pygame.image.load(self.renderer.get_image_path(ph)),
                                 self.resolution)
        self.main_surface = tran_none(self.main_surface, blitdata)

    def show_next(self):
        ph = self.manager.get_next_phenotype(self.renderer.check_image_available)
        self.show_phenotype_image(ph)

if __name__ == '__main__':
    manager = Manager(size=5, min_votes=5, directory=os.getcwd())
    try:
        manager.load()
    except IOError:
        manager.create_from_scratch()
    renderer = ImageRenderer(os.path.join(os.getcwd(), "images"))

    interface = Interface(manager, renderer)
    interface.run()
