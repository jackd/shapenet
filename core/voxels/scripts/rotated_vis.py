#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from shapenet.core.voxels import VoxelConfig
from shapenet.core.blender_renderings.config import RenderConfig
from shapenet.core import cat_desc_to_id
from shapenet.core.voxels.rotated import FrustrumVoxelConfig

cat_desc = 'chair'
base_config = VoxelConfig(voxel_dim=64)
render_config = RenderConfig(shape=(224, 224))
view_index = 1
out_shape = (64,)*3

cat_id = cat_desc_to_id(cat_desc)

frustrum_config = FrustrumVoxelConfig(
    base_config, render_config, view_index, out_shape)
transform = frustrum_config.transformer()


def vis(original, transformed, image):
    import numpy as np
    from mayavi import mlab
    from util3d.mayavi_vis import vis_voxels
    from PIL import Image
    image.show()
    im = np.max(transformed, axis=-1).astype(np.uint8)*255
    # im = im[-1::-1, -1::-1].T
    Image.fromarray(im.T).resize((224, 224)).show()
    mlab.figure()
    vis_voxels(original, color=(0, 0, 1), axis_order='xyz')
    mlab.figure()
    vis_voxels(transformed, color=(0, 1, 0), axis_order='xyz')
    mlab.show()

    # import matplotlib.pyplot as plt
    # transformed = np.max(transformed, axis=-1).astype(np.uint8)*255
    # transformed = transformed[:, -1::-1].T
    # image = np.array(image)
    # plt.figure()
    # plt.imshow(transformed)
    # plt.figure()
    # plt.imshow(image)
    # plt.show()


with base_config.get_dataset(cat_id) as vds:
    with render_config.get_dataset(cat_id, view_index) as rds:
        for example_id in vds:
            original = vds[example_id]
            transformed = transform(original)

            vis(original.dense_data(), transformed, rds[example_id])
