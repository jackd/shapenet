from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from .config import VoxelConfig
from util3d.voxel.binvox import DenseVoxels
from util3d.voxel.manip import OrthographicFiller

# import numpy as np
# _structure = np.zeros((3, 3, 3), dtype=np.bool)
# _structure[1, 1, 1:1] = 1
# _structure[1, 1:1, 1] = 1
# _structure[1:1, 1, 1] = 1


def filled_voxels(voxels_dense):
    from scipy.ndimage.morphology import binary_fill_holes
    _structure = None
    return binary_fill_holes(voxels_dense, _structure)


# class DummyContextWrapper(object):
#     def __init__(self, base):
#         self._base = base
#
#     def __enter__(self):
#         return self._base
#
#     def __exit__(self, *args, **kwargs):
#         pass


# class OrthographicFillerFn(object):
#     def __init__(self, dims):
#         self._dims = dims
#
#     def __enter__(self):
#         self.open()
#         return self
#
#     def __exit__(self, *args, **kwargs):
#         self.exit()
#
#     def open(self):
#         import tensorflow as tf
#         from util3d.voxel.manip_tf import orthographic_filled_voxels
#         graph = tf.Graph()
#         with graph.as_default():
#             self._vox = tf.placeholder(shape=self._dims, dtype=tf.bool)
#             self._out = orthographic_filled_voxels(self._vox)
#
#         self._sess = tf.Session(graph=graph)
#
#     def close(self):
#         self._sess.close()
#         self._sess = None
#
#     def __call__(self, values):
#         return self._sess.run(self._out, feed_dict={self._vox: values})


class FillAlg(object):
    def __init__(self):
        raise RuntimeError('Not meant to be instantiated')

    BASE = 'filled'
    ORTHOGRAPHIC = 'orthographic'


# def get_orthographic_filler(dims):
#     try:
#         return OrthographicFillerFn(dims)
#     except ImportError:
#         from util3d.voxel.manip import OrthographicFiller
#         print('Error importing tensorflow - using numpy implementation')
#         return OrthographicFiller(dims)


_fill_fns = {
    FillAlg.BASE: lambda dims: filled_voxels,
    # FillAlg.ORTHOGRAPHIC: get_orthographic_filler,
    FillAlg.ORTHOGRAPHIC: OrthographicFiller,
}


_algs = (FillAlg.BASE, FillAlg.ORTHOGRAPHIC)


def check_valid_fill_alg(fill_alg):
    if fill_alg not in _algs:
        raise ValueError('Invalid fill_alg "%s": must be one of %s' % _algs)


class FilledVoxelConfig(VoxelConfig):
    def __init__(self, base_config, fill_alg=None):
        if fill_alg is None:
            fill_alg = FillAlg.BASE
        else:
            check_valid_fill_alg(fill_alg)
        self._fill_alg = fill_alg
        self._base_config = base_config
        self._voxel_id = '%s_%s' % (base_config.voxel_id, fill_alg)

    @property
    def voxel_dim(self):
        return self._base_config.voxel_dim

    @property
    def root_dir(self):
        from . import path
        dir = os.path.join(
            path.data_dir, self._fill_alg, self._base_config.voxel_id)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        return dir

    def create_voxel_data(self, cat_id, example_ids=None, overwrite=False):
        from progress.bar import IncrementalBar
        src = self._base_config.get_dataset(cat_id)
        with src:
            if not overwrite:
                if example_ids is None:
                    example_ids = tuple(src.keys())
                path = self.get_binvox_path(cat_id, example_ids[0])

                example_ids = [e for e in example_ids if not os.path.isfile(
                    self.get_binvox_path(cat_id, e))]

            if example_ids is not None:
                src = src.subset(example_ids)
            fill_fn = _fill_fns[self._fill_alg]((self.voxel_dim,)*3)
            # if not hasattr(fill_fn, '__enter__'):
            #     fill_fn = DummyContextWrapper(fill_fn)
            src = src.map(
                lambda v: DenseVoxels(
                    fill_fn(v.dense_data()), scale=v.scale,
                    translate=v.translate))
            folder = self.get_binvox_path(cat_id, None)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            # with fill_fn:
            bar = IncrementalBar(max=len(src))
            for example_id, vox in src.items():
                path = self.get_binvox_path(cat_id, example_id)
                vox.save(path)
                bar.next()
            bar.finish()
