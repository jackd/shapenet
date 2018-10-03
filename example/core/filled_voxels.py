#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from shapenet.core.voxels.config import VoxelConfig
from shapenet.core import cat_desc_to_id
from util3d.mayavi_vis import vis_sliced
from mayavi import mlab
import numpy as np

cat_desc = 'watercraft'
cat_id = cat_desc_to_id(cat_desc)


base = VoxelConfig(voxel_dim=128)
filled = base.filled('orthographic')
with base.get_dataset(cat_id) as bds, filled.get_dataset(cat_id) as fds:
    for example_id in bds:
        base_data = bds[example_id].dense_data()
        filled_data = fds[example_id].dense_data()
        for dense_data in (base_data, filled_data):
            mlab.figure()
            vis_sliced(dense_data.astype(np.float32), axis_order='xyz')
        mlab.show()
        break
