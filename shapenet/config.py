from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import yaml

root_dir = os.path.realpath(os.path.dirname(__file__))
_config_path = os.path.join(root_dir, 'config.yaml')


def _create_config():
    import shutil
    default_config_path = os.path.join(root_dir, 'default_config.yaml')
    if not os.path.isfile(default_config_path):
        raise IOError(
            'No file at default_config_path "%s"' % default_config_path)
    shutil.copyfile(default_config_path, _config_path)


if not os.path.isfile(_config_path):
    _create_config()


def load_config():
    with open(_config_path, 'r') as fp:
        config = yaml.load(fp)
    return config


config = load_config()
