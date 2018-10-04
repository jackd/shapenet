#!/usr/bin/python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from shapenet.r2n2.binvox import BinvoxManager


def vis(vox):
    import numpy as np
    from mayavi import mlab
    voxels = np.pad(
        vox.dense_data(), [[1, 1], [1, 1], [1, 1]], mode='constant')
    mlab.figure()
    mlab.contour3d(
        voxels.astype(np.float32), color=(0, 0, 1), contours=[0.5],
        opacity=0.5)
    mlab.show()


cat_id = '02958343'  # car

with BinvoxManager() as bvm:
    ids = bvm.get_example_ids()
    example_ids = ids[cat_id]
    print(cat_id)
    for example_id in example_ids:
        vox = bvm[cat_id, example_id]
        vis(vox)
