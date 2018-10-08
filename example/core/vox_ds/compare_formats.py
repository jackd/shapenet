#!/usr/bin/python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from shapenet.core.voxels import VoxelConfig
from shapenet.core.voxels.datasets import get_dataset
from shapenet.core import cat_desc_to_id, get_example_ids

# from util3d.voxel import rle as rle
# from util3d.voxel import brle as brle

config = VoxelConfig(voxel_dim=32)
cat_desc = 'cellphone'
cat_id = cat_desc_to_id(cat_desc)
example_ids = get_example_ids(cat_id)

example_index = 10
example_id = example_ids[example_index]


def vis(*dense_data):
    from mayavi import mlab
    from util3d.mayavi_vis import vis_voxels
    for d in dense_data:
        mlab.figure()
        vis_voxels(d, color=(0, 0, 1), axis_order='xyz')
    mlab.show()


out = []

for key in ('file', 'zip', 'rle', 'brle'):
    if key in ('rle', 'brle'):
        kwargs = dict(compression='lzf', pad=True)
    else:
        kwargs = {}
    with get_dataset(
            config, cat_id, id_keys=True, key=key, **kwargs) as ds:
        out.append(ds[example_id].dense_data())


assert(all(np.all(j == out[0]) for j in out[1:]))
vis(out[-1])
