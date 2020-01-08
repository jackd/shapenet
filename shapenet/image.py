from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from PIL import Image

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def load_image_from_file(f):
    return Image.open(StringIO(f.read()))


def load_image_from_zip(zip_file, path):
    with zip_file.open(path) as fp:
        return load_image_from_file(fp)


def with_background(image4d, background_color):
    """Sets background of 4d image to the specified color."""
    image = np.asarray(image4d)
    assert(image.shape[-1] == 4)
    background = image[..., 3] == 0
    image = image[..., :3].copy()
    image[background] = background_color
    return image
