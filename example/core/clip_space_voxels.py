#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
import numpy as np

from shapenet.core.voxels.rotated import FrustrumVoxelConfig
from shapenet.core.blender_renderings import RenderConfig
from shapenet.core.voxels import VoxelConfig
from shapenet.core import cat_desc_to_id

cat_desc = 'chair'
base_config = VoxelConfig(voxel_dim=64)
render_config = RenderConfig(shape=(224, 224))
view_index = 1
out_shape = (32,)*3

cat_id = cat_desc_to_id(cat_desc)

frustrum_config = FrustrumVoxelConfig(
    base_config, render_config, view_index, out_shape)


def vis(base, frust, image):
    from util3d.mayavi_vis import vis_voxels
    from mayavi import mlab
    from PIL import Image
    frust_data = frust.dense_data()
    frust_flat = np.max(frust_data, axis=-1)
    Image.fromarray(
        frust_flat.T.astype(np.uint8)*255).resize((224, 224)).show()

    image.show()
    mlab.figure()
    vis_voxels(base.dense_data(), color=(0, 0, 1))
    mlab.figure()
    vis_voxels(frust_data, color=(0, 1, 0))
    mlab.show()


with frustrum_config.get_dataset(cat_id) as fds:
    with base_config.get_dataset(cat_id) as bds:
        with render_config.get_dataset(cat_id, view_index) as vds:
            example_ids = list(fds.keys())
            random.shuffle(example_ids)
            for example_id in example_ids:
                vis(bds[example_id], fds[example_id], vds[example_id])
