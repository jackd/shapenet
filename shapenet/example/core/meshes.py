#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from shapenet.core.meshes import get_mesh_dataset
from shapenet.core import cat_desc_to_id
from util3d.mayavi_vis import vis_mesh
from mayavi import mlab

desc = 'plane'

cat_id = cat_desc_to_id(desc)
with get_mesh_dataset(cat_id) as mesh_dataset:
    for example_id in mesh_dataset:
        example_group = mesh_dataset[example_id]
        vertices, faces = (
            np.array(example_group[k]) for k in ('vertices', 'faces'))
        vis_mesh(vertices, faces, color=(0, 0, 1), axis_order='xzy')
        mlab.show()
