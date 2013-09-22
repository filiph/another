import os
import subprocess
from PIL import Image
import time
import datetime


import logging
logger = logging.getLogger("another.image_renderer")

__author__ = 'Filip Hracek'

_DEFAULT_RENDER_EXECUTABLE = os.path.dirname(os.path.realpath(__file__)) + "/../render_dna.sh"
_DEFAULT_GIMP_EXECUTABLE = os.path.dirname(os.path.realpath(__file__)) + "/../apply_painting.sh"

class RenderJob:
    RENDER_TIMEOUT = datetime.timedelta(minutes=5)

    def __init__(self, ctx, phenotype):
        self.phenotype = phenotype
        self.render_process = None
        self.gimp_process = None
        self.dev_null = None

        self.ctx = ctx

        self.done = False
        self.done_with_error = False
        # TODO self.cannot_render

    def start(self, on_error=None):
        self.dev_null = open(os.devnull, 'w')
        self.on_error = on_error
        self.start_datetime = datetime.datetime.now()
        self._start_render_process()

    def _start_render_process(self, safe_mode=False):
        self.safe_mode = safe_mode
        try:
            # TODO: set render resolution according to fullscreen resolution
            logger.info("Starting render process for %s.", self.phenotype)
            self.render_process = subprocess.Popen(
                [self.ctx.render_executable, self.phenotype.as_string,
                 self.ctx.construct_image_path(self.phenotype)], stdout=self.dev_null)
        except OSError as e:
            logger.error("Render process for %s failed: %s", self.phenotype, e)
            if callable(self.on_error): self.on_error()
            self.done_with_error = True
            self.stop()

    def _start_gimp_process(self):
        try:
            logger.info("Starting gimp process for %s.", self.phenotype)
            self.gimp_process = subprocess.Popen(
                [self.ctx.gimp_executable, self.ctx.construct_image_path(self.phenotype)],
                stdout=self.dev_null)
        except OSError as e:
            logger.error("Gimp process for %s failed: %s", self.phenotype, e)
            if callable(self.on_error): self.on_error()
            self.done_with_error = True
            self.stop()


    def update(self):
        if self.done:
            return

        past_timeout = datetime.datetime.now() - self.start_datetime > self.RENDER_TIMEOUT
        if past_timeout:
            logger.warning("RenderJob of %s is taking too long. Stopping.", self.phenotype)

        if self.render_process != None:
            return_code = self.render_process.poll()
            if return_code == None and not past_timeout:
                # Process still running.
                pass
            elif return_code != 0 or past_timeout:
                # Process returned with an error or is running too long.
                if not self.safe_mode:
                    logger.warning("Render of %s failed. Restarting in safe mode.",
                                    self.phenotype)
                    self._start_render_process(safe_mode=True)
                else:
                    logger.error("Render of %s failed even in safe mode.", self.phenotype)
                    if callable(self.on_error): self.on_error()
                    self.done_with_error = True
                    self.stop()
            else:
                # Process finished successfully.
                self.render_process = None
                self._start_gimp_process()

        elif self.gimp_process != None:
            return_code = self.gimp_process.poll()
            if return_code == None and not past_timeout:
                # Process still running.
                pass
            elif return_code != 0 or past_timeout:
                # Process returned with an error or is running too long.
                logger.error("Gimp modification of %s failed.", self.phenotype)
                if callable(self.on_error): self.on_error()
                self.done_with_error = True
                self.stop()
            else:
                # Process finished successfully.
                self.gimp_process = None
                self.stop()

    def stop(self):
        if self.render_process != None:
            self._terminate(self.render_process)
            self.render_process = None
        if self.gimp_process != None:
            self._terminate(self.gimp_process)
            self.gimp_process = None
        if self.done_with_error:
            logger.info("Removing image for %s", self.phenotype)
            try:
                os.remove(self.ctx.construct_image_path(self.phenotype))
            except OSError as e:
                logger.error("Couldn't remove non-gimped file because of IO error: %s", e)
        self.dev_null.close()
        self.done = True
        logger.info("Render job finished (%s error)", "with" if self.done_with_error else
        "without")

    def _terminate(self, process):
        logger.info("Terminating process.")
        process.terminate()
        while process.poll() == None:
            time.sleep(0.1)
        logger.info("Process has terminated.")



class ImageRenderer:
    """
    Takes care of rendering images, keeps track of rendering processes, returns file paths.

    Don't forget to call `close()` when finished. This will make sure all renders are properly
    terminated.
    """
    def __init__(self, images_directory, render_executable_path=_DEFAULT_RENDER_EXECUTABLE,
                 gimp_executable_path=_DEFAULT_GIMP_EXECUTABLE):
        self.images_directory = images_directory
        if not os.path.isdir(self.images_directory):
            try:
                os.makedirs(self.images_directory)
            except IOError:
                logger.critical("Images directory %s doesn't exist and couldn't be created.",
                              self.images_directory)
                raise
        self.render_executable = render_executable_path
        if not os.path.isfile(self.render_executable):
            raise Exception("Render bash script file {} doesn't exist".format(
                self.render_executable))
        self.gimp_executable = gimp_executable_path
        if not os.path.isfile(self.gimp_executable):
            raise Exception("Gimp bash script file {} doesn't exist".format(
                self.gimp_executable))

        self.rendered_images = []
        self._check_available_images()

        self.running_jobs = []
        self.render_backlog = []

    IMAGE_EXTENSION = ".jpg"
    MAX_PARALLEL_RENDERS = 1

    def _check_available_images(self):
        for directory, subdirectories, filenames in os.walk(self.images_directory):
            for filename in filenames:
                dna, extension = os.path.splitext(filename)
                if extension != ImageRenderer.IMAGE_EXTENSION:
                    continue

                # TODO use PIL to check if file is proper JPEG: http://stackoverflow.com/a/266731
                self.rendered_images.append(os.path.join(directory, filename))

    def construct_image_path(self, ph):
        return os.path.join(self.images_directory, "generation{}".format(ph.generation),
                            "{}{}".format(ph.as_string, ImageRenderer.IMAGE_EXTENSION))

    def check_image_available(self, ph):
        return self.construct_image_path(ph) in self.rendered_images

    def get_image_path(self, ph):
        """
        Returns image path or None if image is not (yet) rendered.
        """
        if self.check_image_available(ph):
            return self.construct_image_path(ph)
        else:
            return None


    def start_image_render(self, ph):
        """
        Starts a new process for rendering the image associated with the Phenotype. Returns True
        if a new process has been started, False if the image already exists or the process
        is already running.
        :param ph: Phenotype to render.
        """
        if self.check_image_available(ph):
            # Image already exists.
            return False
        if ph in [job.phenotype for job in self.running_jobs]:
            # Image already being rendered.
            return False
        if self.check_image_renders() < ImageRenderer.MAX_PARALLEL_RENDERS:
            job = RenderJob(self, ph)
            def on_error():
                # Stillborn phenotype.
                ph.no = 1000 # TODO: make this more meaningful.
                # TODO: Count job failures. When a lot of them, try rebooting?
            job.start(on_error=on_error)
            self.running_jobs.append(job)
            return True
        else:
            logger.info("Adding render job of %s to backlog (too many processes currently "
                         "running).", ph)
            self.render_backlog.append(ph)
            return True

    @property
    def is_working(self):
        return len(self.running_jobs) > 0 or len(self.render_backlog) > 0

    def check_image_renders(self):
        """ Checks the status of background image renders. Returns number of running processes. """
        count = 0
        for job in self.running_jobs:
            job.update()
            if job.done:
                self.running_jobs.remove(job)
                if not job.done_with_error:
                    self.rendered_images.append(self.construct_image_path(job.phenotype))
                if self.render_backlog:
                    self.start_image_render(self.render_backlog.pop(0))
                    count += 1
            else:
                count += 1
        return count

    def wait_until_done(self):
        while self.check_image_renders() > 0:
            time.sleep(0.1)

    def close(self):
        self.render_backlog.clear()
        for job in self.running_jobs:
            job.stop()
        self.running_jobs.clear()