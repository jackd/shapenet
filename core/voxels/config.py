from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from . import path
from .. import get_example_ids


class VoxelConfig(object):
    def __init__(
            self, voxel_dim=32, exact=True, dc=True, aw=True, c=False,
            v=False):
        self._voxel_dim = voxel_dim
        self._exact = exact
        self._dc = dc
        self._aw = aw
        self._c = c
        self._v = v
        self._voxel_id = path.get_voxel_id(
            voxel_dim, exact=exact, dc=dc, aw=aw, c=c, v=v)

    def filled(self, fill_alg=None):
        from .filled import FilledVoxelConfig
        return FilledVoxelConfig(self, fill_alg)

    @property
    def voxel_dim(self):
        return self._voxel_dim

    @property
    def exact(self):
        return self._exact

    @property
    def dc(self):
        return self._dc

    @property
    def aw(self):
        return self._aw

    @property
    def c(self):
        return self._c

    @property
    def v(self):
        return self._v

    @property
    def voxel_id(self):
        return self._voxel_id

    def get_binvox_subpath(self, cat_id, example_id):
        return path.get_binvox_subpath(cat_id, example_id)

    def get_binvox_path(self, cat_id, example_id):
        return os.path.join(
            self.root_dir, self.get_binvox_subpath(cat_id, example_id))

    @property
    def root_dir(self):
        return path.get_binvox_dir(self.voxel_id)

    def create_voxel_data(self, cat_id, example_ids=None, overwrite=False):
        from progress.bar import IncrementalBar
        from util3d.voxel.convert import obj_to_binvox
        from .. import objs
        if example_ids is None:
            example_ids = get_example_ids(cat_id)

        kwargs = dict(
            voxel_dim=self.voxel_dim,
            exact=self.exact,
            dc=self.dc,
            aw=self.aw,
            c=self.c,
            v=self.v,
            overwrite_original=True)

        path_ds = objs.get_extracted_obj_path_dataset(cat_id)
        bvd = self.get_binvox_path(cat_id, None)
        if not os.path.isdir(bvd):
            os.makedirs(bvd)

        with path_ds:
            print('Creating binvox voxel data')
            bar = IncrementalBar(max=len(example_ids))
            for example_id in example_ids:
                bar.next()
                binvox_path = self.get_binvox_path(cat_id, example_id)
                if overwrite or not os.path.isfile(binvox_path):
                    obj_path = path_ds[example_id]
                    obj_to_binvox(obj_path, binvox_path, **kwargs)
        bar.finish()

    def get_dataset(self, cat_id):
        from .datasets import get_dataset
        print(
            'Warning: voxel_config.get_dataset deprecated. '
            'Use voxels.datasets.get_dataset instead')
        return get_dataset(self, cat_id, key='zip')


def get_base_config(voxel_dim):
    return VoxelConfig(voxel_dim)


def get_alt_config(voxel_dim):
    return VoxelConfig(
        voxel_dim, exact=False, dc=False, aw=False, c=True, v=True)


def get_config(voxel_dim, alt=False):
    if alt:
        return get_alt_config(voxel_dim)
    else:
        return get_base_config(voxel_dim)
