from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import yaml
import numpy as np
from .manager import WritableViewManager


class TxtViewManager(WritableViewManager):
    def __init__(self, root_folder):
        self._root_folder = root_folder

    @property
    def root_folder(self):
        return self._root_folder

    def view_params_path(self):
        return os.path.join(self.root_folder, 'view_params.yaml')

    def has_view_params(self):
        return os.path.isfile(self.view_params_path())

    def camera_positions_path(self, cat_id, example_id):
        return os.path.join(
            self.root_folder, 'camera_positions', cat_id,
            '%s.txt' % example_id)

    def get_view_params(self):
        path = self.view_params_path()
        with open(path, 'r') as fp:
            return yaml.load(fp)

    def get_camera_positions(self, cat_id, example_id):
        return np.loadtxt(self.camera_positions_path(cat_id, example_id))

    def set_view_params(self, **params):
        with open(self.view_params_path(), 'w') as fp:
            yaml.dump(params, fp, default_flow_style=False)

    def set_camera_positions(self, cat_id, example_id, camera_pos):
        path = self.camera_positions_path(cat_id, example_id)
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return np.savetxt(path, camera_pos)

    def get_cat_ids(self):
        return os.listdir(os.path.join(self.root_folder, 'camera_positions'))

    def get_example_ids(self, cat_id):
        return (
            k[:-4] for k in os.listdir(
                os.path.join(self.root_folder, 'camera_positions', cat_id)))


def get_base_txt_manager_dir(turntable=False, n_views=24):
    from .. import path
    from .base import get_base_id
    manager_id = get_base_id(turntable, n_views)
    return path.get_data_dir('views', manager_id)


def get_base_txt_manager(turntable=False, n_views=24):
    from .txt import TxtViewManager
    root_folder = get_base_txt_manager_dir(turntable, n_views)
    manager = TxtViewManager(root_folder)
    if not manager.has_view_params():
        from .lazy import get_base_lazy_manager
        manager.copy_from(get_base_lazy_manager(turntable, n_views))
    return manager
