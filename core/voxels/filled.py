from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from .config import VoxelConfig
from util3d.voxel.binvox import DenseVoxels
# import numpy as np
# _structure = np.zeros((3, 3, 3), dtype=np.bool)
# _structure[1, 1, 1:1] = 1
# _structure[1, 1:1, 1] = 1
# _structure[1:1, 1, 1] = 1


def filled_voxels(voxels_dense):
    from scipy.ndimage.morphology import binary_fill_holes
    _structure = None
    return binary_fill_holes(voxels_dense, _structure)


class FilledVoxelConfig(VoxelConfig):
    def __init__(self, base_config):
        self._base_config = base_config
        self._voxel_id = '%s_filled' % base_config.voxel_id

    @property
    def voxel_dim(self):
        return self._base_config.voxel_dim

    @property
    def root_dir(self):
        from . import path
        dir = os.path.join(path.data_dir, 'filled', self._base_config.voxel_id)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        return dir

    def create_voxel_data(self, cat_id, example_ids=None, overwrite=False):
        from progress.bar import IncrementalBar
        src = self._base_config.get_dataset(cat_id)
        if example_ids is not None:
            src = src.subset(example_ids)
        src = src.map(
            lambda v: DenseVoxels(filled_voxels(
                v.dense_data()), scale=v.scale, translate=v.translate))
        with src:
            bar = IncrementalBar(max=len(src))
            folder = self.get_binvox_path(cat_id, None)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            for example_id, vox in src.items():
                path = self.get_binvox_path(cat_id, example_id)
                vox.save(path)
                bar.next()
            bar.finish()
