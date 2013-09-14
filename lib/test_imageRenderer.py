import os
import shutil
from unittest import TestCase
import time
from lib.image_renderer import ImageRenderer
import tempfile
from PIL import Image
from lib.phenotype import Phenotype

import logging
logging.basicConfig(level=logging.DEBUG)

__author__ = 'Filip Hracek'


class TestImageRenderer(TestCase):
    def test_no_files_in_images_dir(self):
        images_dir = tempfile.mkdtemp()
        renderer = ImageRenderer(images_dir)
        self.assertListEqual(renderer.rendered_images, [])
        renderer.close()
        shutil.rmtree(images_dir)

    def test_jpeg_file_in_images_dir(self):
        images_dir = tempfile.mkdtemp()
        image = Image.new("RGB", (800, 600), (0, 0, 0))
        image_filename = os.path.join(images_dir, "0{}".format(ImageRenderer.IMAGE_EXTENSION))
        image.save(image_filename)
        renderer = ImageRenderer(images_dir)
        self.assertIn(image_filename, renderer.rendered_images)
        renderer.close()
        shutil.rmtree(images_dir)

    def test_start_render(self):
        images_dir = tempfile.mkdtemp()
        renderer = ImageRenderer(images_dir)
        ph = Phenotype(-1)
        ph.randomize()
        ph.as_string = "1" * len(ph.as_string)  # set DNA to "1111111...111"
        self.assertFalse(renderer.check_image_available(ph))
        self.assertEqual(len(renderer.running_jobs), 0)
        renderer.start_image_render(ph)
        self.assertEqual(len(renderer.running_jobs), 1)
        self.assertTrue(renderer.is_working)
        while renderer.is_working:
            time.sleep(0.1)
            renderer.check_image_renders()
        self.assertTrue(renderer.check_image_available(ph))
        self.assertEqual(len(renderer.running_jobs), 0)
        renderer.close()
        shutil.rmtree(images_dir)

    def test_renderer_close(self):
        images_dir = tempfile.mkdtemp()
        renderer = ImageRenderer(images_dir)
        ph = Phenotype(-1)
        ph.randomize()
        ph.as_string = "1" * len(ph.as_string)  # set DNA to "1111111...111"
        renderer.start_image_render(ph)
        self.assertTrue(renderer.is_working)
        time.sleep(0.1)
        renderer.check_image_renders()
        job = renderer.running_jobs[0]
        self.assertTrue(renderer.is_working)
        renderer.close()
        time.sleep(0.1)
        self.assertFalse(renderer.is_working)
        shutil.rmtree(images_dir)
