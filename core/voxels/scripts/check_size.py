#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np
import h5py
from progress.bar import IncrementalBar
import util3d.voxel.rle as rle
from shapenet.core import get_cat_ids
from shapenet.core.voxels import VoxelConfig
from shapenet.core.voxels.filled import FillAlg

delete_src = True
cat_ids = get_cat_ids()


def has_data(config):
    for cat_id in cat_ids:
        if os.path.isfile(config.get_hdf5_path(cat_id)):
            yield cat_id


configs = []
for dim in (32, 64, 128, 256):
    base = VoxelConfig(dim)
    configs.append(base)
    for alg in (FillAlg.BASE, FillAlg.ORTHOGRAPHIC):
        configs.append(base.filled(alg))

pairs = []
for config in configs:
    for cat_id in has_data(config):
        pairs.append((config, cat_id))


n = len(pairs)
print('Checking %d pairs' % n)
for i, (config, cat_id) in enumerate(pairs):
    print('%s - %s : %d / %d' % (config.voxel_id, cat_id, i+1, n))
    with h5py.File(config.get_hdf5_path(cat_id), 'a') as root:
        rle_data = root['rle_data']
        nz = config.voxel_dim**3
        nd = len(rle_data)
        bar = IncrementalBar(max=nd)
        for i in range(nd):
            bar.next()
            le = rle.length(np.array(rle_data[i]))
            if le != nz:
                print('**')
                rle_data[i] = rle.zeros(nz)
        bar.finish()
