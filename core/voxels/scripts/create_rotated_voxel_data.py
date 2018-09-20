#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import shutil
from shapenet.core.voxels import VoxelConfig
from shapenet.core.blender_renderings.config import RenderConfig
from shapenet.core import cat_desc_to_id
from shapenet.core.voxels.rotated import FrustrumVoxelConfig

cat_desc = 'chair'
base_config = VoxelConfig(voxel_dim=128)
render_config = RenderConfig(shape=(224, 224))
out_shape = (28,)*3

cat_id = cat_desc_to_id(cat_desc)

for view_index in range(render_config.n_images):
    frustrum_config = FrustrumVoxelConfig(
        base_config, render_config, view_index, out_shape)
    frustrum_config.create_voxel_data(cat_id)
    frustrum_config = FrustrumVoxelConfig(
        base_config, render_config, view_index, out_shape)
    frustrum_config.create_zip_file(cat_id)
    shutil.rmtree(frustrum_config.get_binvox_path(cat_id, None))
