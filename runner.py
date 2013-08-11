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

FULLSCREEN = False
RESOLUTION = (800, 600)
PATH_TO_SCRIPT = os.path.dirname(os.path.realpath(__file__))
PATH_TO_POP_DUMP = PATH_TO_SCRIPT + "/population.dump"
PATH_TO_RENDER_SH = PATH_TO_SCRIPT + "/dnarender.sh"

class Runner:
    def __init__(self):
        self.running_procs = []
        self.render_backlog = []

        self.fullscreen = FULLSCREEN
        self.resolution = RESOLUTION


    def init_pop(self):
        try:
            with open(PATH_TO_POP_DUMP, "rb") as f:
                self.pop = pickle.load(f)
                print("Population loaded from " + PATH_TO_POP_DUMP)
        except IOError:
            print("Population file not found. Creating first generation.")
            self.pop = Population()
            self.pop.create_first_generation()
            for ph in self.pop.phenotypes:
                self.start_image_render(ph)
            sys.stdout.write("Waiting for render of first batch to end")
            sys.stdout.flush()
            while self.check_image_renders() > 0:
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(1)


    RENDER_TIMEOUT = 60
    MAX_PARALLEL_RENDERS = 2

    def start_image_render(self, ph):
        if self.check_image_available(ph):
            return
        if self.check_image_renders() <= Runner.MAX_PARALLEL_RENDERS:
            try:
                FNULL = open(os.devnull, 'w')
                # TODO: set render resolution according to fullscreen resolution
                proc = subprocess.Popen([PATH_TO_RENDER_SH, ph.get_binary_string(), 
                    self.get_phenotype_image_path(ph)], stdout=FNULL)
                        #stderr=subprocess.PIPE
                self.running_procs.append(proc)
            except OSError as e:
                print(str(e))
                raise
        else:
            self.render_backlog.append(ph)

    def check_image_renders(self):
        """ Checks the status of background image renders. Returns number of running processes. """
        count = 0
        for proc in self.running_procs:
            retcode = proc.poll()
            if retcode is not None:  # process finished
                self.running_procs.remove(proc)
                if retcode != 0:
                    print("ERROR: Render process failed")
                    print(proc.stderr)
                    # TODO: do something about it
                else:
                    print("Render process finished successfully.")
                if self.render_backlog:
                    self.start_image_render(self.render_backlog.pop(0))
            else:  # process still running
                count += 1
        return count


    def save_pop_to_file(self):
        print("Trying to save population...")
        try:
            with open(PATH_TO_POP_DUMP, "wb") as f:
                pickle.dump(self.pop, f)
                print("Population saved to " + PATH_TO_POP_DUMP)
        except IOError:
            print("ERROR: Couldn't write population to file.")
            raise

    def get_phenotype_image_path(self, ph):
        # TODO: better
        return PATH_TO_SCRIPT + "/generation" + str(ph.generation) + "/" + ph.get_binary_string() + ".jpg"

    def check_image_available(self, ph):
        # TODO: check against a list (cached)
        return os.path.isfile(self.get_phenotype_image_path(ph))

    def run(self):
        ## Initialize PyGame
        pygame.display.init()
        if self.fullscreen:
            self.resolution = pygame.display.list_modes()[0]
            self.main_surface = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        else:
            self.main_surface = pygame.display.set_mode(self.resolution)
        pygame.display.update()

        self.show_phenotype_image(self.pop.current)

        while True:
            for event in pygame.event.get():
                if (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                    self.save_pop_to_file()
                    pygame.quit()
                    return 0
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                    self.pop.current.yes += 1
                    self.check_image_renders()
                    ph = self.pop.get_next(self.check_image_available)
                    self.show_phenotype_image(ph)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    self.pop.current.no += 1
                    self.check_image_renders()
                    ph = self.pop.get_next(self.check_image_available)
                    self.show_phenotype_image(ph)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.pop.current.meh += 1
                    self.check_image_renders()
                    ph = self.pop.get_next(self.check_image_available)
                    self.show_phenotype_image(ph)

                    # TODO: find better place for this (auto-advance)
                    if self.pop.is_ready_for_next_generation():
                        children = self.pop.create_new_generation()
                        for child in children:
                            child.mutate(0.1)
                            self.start_image_render(child)


                # elif event.type == pygame.USEREVENT + 1:
                #     i += 1
                #     if i >= len(images):
                #         i = 0
                #     save_pop_to_file()

    def show_phenotype_image(self, ph):
        print("Showing phenotype " + str(ph.idn) + " (gen " + str(ph.generation) +
                ", dna " + ph.get_binary_string() + ")")
        blitdata = rationalSizer(pygame.image.load(self.get_phenotype_image_path(ph)), self.resolution)
        self.main_surface = tran_none(self.main_surface, blitdata)

if __name__ == '__main__':
    runner = Runner()
    runner.init_pop()
    runner.run()
