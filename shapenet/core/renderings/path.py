from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os


renderings_format = 'r%03d%s.png'


def get_rendering_filename(view_index, suffix=''):
    return renderings_format % (view_index, suffix)


def get_rendering_subpath(cat_id, example_id, view_index):
    return os.path.join(
        get_renderings_subdir(cat_id, example_id),
        get_rendering_filename(view_index))


def get_renderings_subdir(cat_id, example_id=None):
    if example_id is None:
        return cat_id
    else:
        return os.path.join(cat_id, example_id)
