#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
import numpy as np
from mayavi import mlab
from util3d.mayavi_vis import vis_point_cloud, vis_normals
from shapenet.core.point_clouds import get_point_cloud_dataset
from shapenet.core.point_clouds import get_cloud_normal_dataset
from shapenet.core import cat_desc_to_id

cat_desc = 'plane'
n_points = 16384
cat_id = cat_desc_to_id(cat_desc)

show_normals = True
if vis_normals:
    dataset = get_cloud_normal_dataset(cat_id, n_points)
else:
    dataset = get_point_cloud_dataset(cat_id, n_points)

with dataset:
    for example_id in dataset:
        data = dataset[example_id]
        s = random.sample(range(n_points), 1024)
        if show_normals:
            cloud = np.array(data['points'])
            normals = np.array(data['normals'])
            cloud = cloud[s]
            normals = normals[s]
        else:
            cloud = np.array(data)
            normals = None
            cloud = cloud[s]
        vis_point_cloud(
            cloud, axis_order='xzy', color=(0, 0, 1), scale_factor=0.002)
        if normals is not None:
            vis_normals(cloud, normals, scale_factor=0.01, axis_order='xzy')
        mlab.show()
