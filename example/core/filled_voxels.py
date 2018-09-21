#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from shapenet.core.voxels.config import VoxelConfig
from shapenet.core.voxels.filled import filled_voxels
from shapenet.core import cat_desc_to_id
from util3d.mayavi_vis import vis_sliced
from mayavi import mlab
import numpy as np

cat_desc = 'chair'
cat_id = cat_desc_to_id(cat_desc)


config = VoxelConfig(voxel_dim=32)
with config.get_dataset(cat_id) as ds:
    for example_id in ds:
        dense_data = ds[example_id].dense_data()
        filled = filled_voxels(dense_data)
        for vox in (dense_data, filled):
            mlab.figure()
            vis_sliced(vox.astype(np.float32), axis_order='xyz')
        mlab.show()
        break


with config.filled().get_dataset(cat_id) as ds:
    for example_id in ds:
        filled = ds[example_id].dense_data()
        mlab.figure()
        vis_sliced(vox.astype(np.float32), axis_order='xyz')
        mlab.show()
        break
