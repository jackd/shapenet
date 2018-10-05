#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from mayavi import mlab
from shapenet.core.voxels.config import get_config
from shapenet.core import cat_desc_to_id, get_example_ids
from util3d.mayavi_vis import vis_sliced
from util3d.mayavi_vis import vis_contours
# from util3d.mayavi_vis import vix_voxels

cat_desc = 'car'
voxel_dim = 256
# alt = True
# voxel_dim = 32
cat_id = cat_desc_to_id(cat_desc)
example_ids = get_example_ids(cat_id)

config = get_config(voxel_dim, alt=False).filled('orthographic')
with config.get_dataset(cat_id) as dataset:
    for example_id in example_ids:
        voxels = dataset[example_id]
        mlab.figure()
        dense = voxels.dense_data()
        # vis_voxels(
        #     dense, color=(0, 0, 1), axis_order='xyz',
        #     scale_factor=0.5)
        # mlab.figure()
        vis_sliced(dense, axis_order='xyz')
        mlab.figure()
        vis_contours(dense, contours=[0.5])
        mlab.show()
