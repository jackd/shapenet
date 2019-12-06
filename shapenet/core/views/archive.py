from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import zipfile
import numpy as np
import yaml
from .manager import ViewManager


class ArchiveViewManager(ViewManager):
    def __init__(self, archive):
        self.archive = archive

    def view_params_subpath(self):
        return 'view_params.yaml'

    def camera_positions_subpath(self, cat_id, example_id):
        return os.path.join('camera_positions', cat_id, '%s.txt' % example_id)

    def open(self, subpath):
        raise NotImplementedError('Abstract method')

    def list_contents(self):
        raise NotImplementedError('Abstract method')

    def get_view_params(self):
        return yaml.load(self.open(self.view_params_subpath()))

    def get_camera_positions(self, cat_id, example_id):
        return np.loadtxt(
            self.open(self.camera_positions_subpath(cat_id, example_id)))

    def get_example_ids(self, cat_id):
        return [
            k.split('/')[2] for k in self.list_contents()
            if k.startswith('camera_positions/%s/' % cat_id)]

    def get_cat_ids(self):
        split_contents = (k.split('/') for k in self.list_contents())
        split_contents = (k for k in split_contents if len(k) == 3)
        return sorted(set(k[1] for k in split_contents))


class ZipViewManager(ArchiveViewManager):
    def open(self, subpath):
        return self.archive.open(subpath)

    def list_contents(self):
        return self.archive.namelist()


def get_base_zip_path(turntable=False, n_views=24):
    import os
    from ..path import get_data_dir
    from .base import get_base_id
    return os.path.join(
        get_data_dir('views'), '%s.zip' % get_base_id(turntable, n_views))


def get_base_zip_manager(turntable=False, n_views=24):
    path = get_base_zip_path(turntable=turntable, n_views=n_views)
    if not os.path.isfile(path):
        from .txt import get_base_txt_manager
        import shutil
        txt = get_base_txt_manager(turntable=turntable, n_views=n_views)
        shutil.make_archive(path[:-4], 'zip', txt.root_folder)
    return ZipViewManager(zipfile.ZipFile(path, 'r'))
