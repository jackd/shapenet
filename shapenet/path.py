from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from .config import config

root_dir = os.path.realpath(os.path.dirname(__file__))


def get_data_dir(*args):
    data_path = config['created_data_dir']
    if data_path.startswith('/') or data_path.startswith('~'):
        folder = os.path.join(data_path, *args)
    else:
        if data_path.startswith('./'):
            data_path = data_path[2:]
        folder = os.path.join(root_dir, data_path, *args)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return folder
