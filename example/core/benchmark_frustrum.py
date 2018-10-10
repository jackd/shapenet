#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from util3d.transform.frustrum import voxel_values_to_frustrum
from util3d.transform.nonhom import get_eye_to_world_transform
from util3d.voxel.binvox import DenseVoxels
from shapenet.core import get_example_ids, to_cat_id
from shapenet.core.renderings.render_manager import get_base_manager
from shapenet.core.voxels.config import get_config
from shapenet.core.voxels.datasets import get_dataset as get_voxel_dataset

import time


cat = 'plane'
voxel_dim = 64
ray_shape = (32,)*3
view_index = 0
cat_id = to_cat_id(cat)
config = get_config(voxel_dim, alt=False).filled('orthographic')
voxel_dataset = get_voxel_dataset(
    config, cat_id, id_keys=True, key='rle', compression='lzf')
image_manager = get_base_manager(dim=256)
n_renderings = image_manager.get_render_params()['n_renderings']
f = 32 / 35


example_ids = get_example_ids(cat_id)
with voxel_dataset:
    for example_id in example_ids:
        start = time.time()
        dense_data = voxel_dataset[example_id].dense_data()
        dense_data = dense_data[:, -1::-1]

        key = (cat_id, example_id)
        eyes = image_manager.get_camera_positions(key)
        for vi in range(n_renderings):
            eye = eyes[vi]
            n = np.linalg.norm(eye)
            R, t = get_eye_to_world_transform(eye)
            z_near = n - 0.5
            z_far = z_near + 1

            frust, inside = voxel_values_to_frustrum(
                dense_data, R, t, f, z_near, z_far, ray_shape,
                include_corners=False)
            frust[np.logical_not(inside)] = 0
            frust = frust[:, -1::-1]
            vox = DenseVoxels(frust)
            rle = vox.rle_data()
        print(time.time() - start)
