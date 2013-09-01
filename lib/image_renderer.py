import os
import subprocess
from PIL import Image

__author__ = 'Filip Hracek'

_DEFAULT_RENDER_EXECUTABLE = os.path.dirname(os.path.realpath(__file__)) + "/../render_dna.sh"


class ImageRenderer:
    """
    Takes care of rendering images, keeps track of rendering processes, returns file paths.
    """
    def __init__(self, images_directory, render_executable_path=_DEFAULT_RENDER_EXECUTABLE):
        self.images_directory = images_directory
        if not os.path.isdir(self.images_directory):
            try:
                os.makedirs(self.images_directory)
            except IOError:
                print("ERROR: Images directory {} doesn't exist and couldn't be created.".format(
                    self.images_directory))
                raise
        self.render_executable = render_executable_path
        if not os.path.isfile(self.render_executable):
            raise Exception("Render bash script file {} doesn't exist".format(
                self.render_executable))

        self.rendered_images = []
        self._check_available_images()

        self.running_procs = []
        self.render_backlog = []

    IMAGE_EXTENSION = ".jpg"
    RENDER_TIMEOUT = 60
    MAX_PARALLEL_RENDERS = 2

    def _check_available_images(self):
        for directory, subdirectories, filenames in os.walk(self.images_directory):
            for filename in filenames:
                dna, extension = os.path.splitext(filename)
                if extension != ImageRenderer.IMAGE_EXTENSION:
                    continue

                # TODO use PIL to check if file is proper JPEG: http://stackoverflow.com/a/266731
                self.rendered_images.append(os.path.join(directory, filename))

    def _construct_image_path(self, ph):
        return os.path.join(self.images_directory, "generation{}".format(ph.generation),
                            "{}{}".format(ph.as_string, ImageRenderer.IMAGE_EXTENSION))

    def check_image_available(self, ph):
        return self._construct_image_path(ph) in self.rendered_images

    def get_image_path(self, ph):
        """
        Returns image path or None if image is not (yet) rendered.
        """
        if self.check_image_available(ph):
            return self._construct_image_path(ph)
        else:
            return None


    def start_image_render(self, ph):
        """
        Starts a new process for rendering the image associated with the Phenotype. Returns True
        if a new process has been started, False if the image already exists or the process
        is already running.
        :param ph: Phenotype to render.
        """
        print("Start render of phenotype " + str(ph.idn))
        if self.check_image_available(ph):
            print("- image already exists")
            return False
        if ph in [ph for ph, proc in self.running_procs]:
            print("- image already being rendered")
            return False
        if self.check_image_renders() < ImageRenderer.MAX_PARALLEL_RENDERS:
            try:
                FNULL = open(os.devnull, 'w')
                # TODO: set render resolution according to fullscreen resolution
                proc = subprocess.Popen([self.render_executable, ph.as_string,
                    self._construct_image_path(ph)], stdout=FNULL)
                        #stderr=subprocess.PIPE
                self.running_procs.append((ph, proc))
                print("- process started")
            except OSError as e:
                print(str(e))
                raise
            return True
        else:
            print("- too many processes running, added to backlog")
            self.render_backlog.append(ph)
            return True

    @property
    def is_working(self):
        return len(self.running_procs) > 0 or len(self.render_backlog) > 0

    def check_image_renders(self):
        """ Checks the status of background image renders. Returns number of running processes. """
        count = 0
        for ph, proc in self.running_procs:
            retcode = proc.poll()
            if retcode is not None:  # process finished
                self.running_procs.remove((ph, proc))
                if retcode != 0:
                    print("ERROR: Render process failed")
                    print(proc.stderr)
                    # TODO: do something about it
                else:
                    print("Render process for {} finished successfully.".format(ph))
                    self.rendered_images.append(self._construct_image_path(ph))
                if self.render_backlog:
                    self.start_image_render(self.render_backlog.pop(0))
            else:  # process still running
                count += 1
        return count

