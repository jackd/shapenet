#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from util3d.transform.frustrum import voxel_values_to_frustrum
from util3d.transform.nonhom import get_eye_to_world_transform
from shapenet.core import get_example_ids, to_cat_id
from shapenet.core.renderings.renderings_manager import get_base_manager
from shapenet.core.voxels.config import get_config
from shapenet.core.voxels.datasets import get_dataset as get_voxel_dataset


cat = 'plane'
voxel_dim = 256
ray_shape = (256,)*3
view_index = 0
cat_id = to_cat_id(cat)
config = get_config(voxel_dim, alt=False).filled('orthographic')
voxel_dataset = get_voxel_dataset(
    config, cat_id, id_keys=True, key='rle', compression='lzf')
image_manager = get_base_manager(dim=256)
f = 32 / 35


def vis(dense_data, image_path, frust):
    from PIL import Image
    from mayavi import mlab
    from util3d.mayavi_vis import vis_contours
    image = Image.open(image_path)
    image.show()
    frust = Image.fromarray(frust).resize(image.size)
    frust.show()
    combined = np.array(image) // 2 + np.array(frust)[:, :, np.newaxis] // 2
    Image.fromarray(combined).show()
    mlab.figure()
    vis_contours(dense_data, contours=[0.5])
    mlab.show()


example_ids = get_example_ids(cat_id)
with voxel_dataset:
    for example_id in example_ids:
        dense_data = voxel_dataset[example_id].dense_data()
        dense_data = dense_data[:, -1::-1]

        key = (cat_id, example_id)
        eyes = image_manager.get_camera_positions(key)
        image_path = image_manager.get_rendering_path(key, view_index)

        eye = eyes[view_index]
        n = np.linalg.norm(eye)
        R, t = get_eye_to_world_transform(eye)
        z_near = n - 0.5
        z_far = z_near + 1

        frust, inside = voxel_values_to_frustrum(
            dense_data, R, t, f, z_near, z_far, ray_shape,
            include_corners=False)
        frust[np.logical_not(inside)] = 0
        frust_image = np.any(frust, axis=-1).T
        frust_image = frust_image[-1::-1].astype(np.uint8)*255
        vis(dense_data, image_path, frust_image)
