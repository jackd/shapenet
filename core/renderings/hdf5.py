from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import h5py
import numpy as np


def create_camera_positions(
        manager, cats=None, compression='lzf', path=None):
    from progress.bar import IncrementalBar
    from shapenet.core import get_example_ids
    from shapenet.core import to_cat_id
    if cats is None:
        from shapenet.r2n2 import get_cat_ids
        cat_ids = get_cat_ids()
    else:
        cat_ids = tuple(to_cat_id(cat) for cat in cats)
    n_renderings = manager.get_render_params()['n_renderings']
    if path is None:
        path = get_camera_positions_path(manager)
    with h5py.File(path, 'a') as base:
        nc = len(cat_ids)
        for ci, cat_id in enumerate(cat_ids):
            print(
                'Creating camera positions archive: cat %d / %d' % (ci+1, nc))
            example_ids = get_example_ids(cat_id)
            n = len(example_ids)
            group = base.require_dataset(
                cat_id, shape=(n, n_renderings, 3), dtype=np.float32)
            bar = IncrementalBar(max=n)
            for i, example_id in enumerate(example_ids):
                group[i] = manager.get_camera_positions((cat_id, example_id))
                bar.next()
            bar.finish()


def get_camera_positions_path(manager):
    return os.path.join(manager.root_dir, 'camera_positions.hdf5')


def get_camera_positions(manager, mode='r'):
    return h5py.File(get_camera_positions_path(manager), mode=mode)
