#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from mayavi import mlab
from shapenet.core.voxels.config import get_config
from shapenet.core.voxels.datasets import get_dataset
from shapenet.core.blender_renderings import RenderConfig
from shapenet.core import to_cat_id, get_example_ids
from util3d.mayavi_vis import vis_sliced
from util3d.mayavi_vis import vis_contours
# from util3d.mayavi_vis import vix_voxels

cat = 'plane'
voxel_dim = 128
alt = False
fill = 'orthographic'
ds_kwargs = dict(key='rle', compression='lzf', shape_key='pad')

# cat = 'pistol'
# voxel_dim = 32
# alt = True
# fill = None
# ds_kwargs = dict(key='zip')

cat_id = to_cat_id(cat)
example_ids = get_example_ids(cat_id)
config = get_config(voxel_dim, alt=alt)
if fill is not None:
    config = config.filled(fill)
with get_dataset(config, cat_id, **ds_kwargs) as dataset:
    with RenderConfig(shape=(256, 256), n_images=8).get_dataset(
            cat_id, view_index=5) as render_ds:
        for example_id in example_ids:
            dense = dataset[example_id].dense_data()
            render_ds[example_id].show()
            mlab.figure()
            vis_sliced(dense, axis_order='xyz')
            mlab.figure()
            vis_contours(dense, contours=[0.5])
            mlab.show()
