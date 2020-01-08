#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from shapenet.core import to_cat_id, get_example_ids
from shapenet.core.renderings.archive_manager import get_archive
from shapenet.core.renderings.renderings_manager import get_base_manager
from shapenet.core.renderings.frustrum_voxels import get_frustrum_voxels_data
from shapenet.core.renderings.frustrum_voxels import GROUP_KEY
from shapenet.core.voxels import get_config


def vis(image_fp, rle_data, out_dim):
    import numpy as np
    from PIL import Image
    from util3d.voxel.binvox import RleVoxels
    from util3d.mayavi_vis import vis_voxels
    from mayavi import mlab
    im = Image.open(image_fp)
    im.show()
    dense_data = RleVoxels(np.array(rle_data), (out_dim,)*3).dense_data()
    sil = np.any(dense_data, axis=-1).T.astype(np.uint8)*255
    sil = Image.fromarray(sil).resize(im.size)
    sil.show()
    comb = np.array(im) // 2 + np.array(sil)[:, :, np.newaxis] // 2
    Image.fromarray(comb).show()
    vis_voxels(dense_data, color=(0, 0, 1))
    mlab.show()


image_dim = 256

src_voxel_dim = 256
out_dim = 32
n_renderings = 24
cat = 'car'

cat_id = to_cat_id(cat)
example_ids = get_example_ids(cat_id)

renderings_manager = get_base_manager(image_dim, n_renderings=n_renderings)
src_config = get_config(src_voxel_dim, alt=False).filled('orthographic')
view_index = 10
with get_archive(renderings_manager, cat_id).get_open_file() as zf:
    with get_frustrum_voxels_data(
            renderings_manager.root_dir, src_config, out_dim, cat_id) as vd:
        rle_data = vd[GROUP_KEY]
        for i, example_id in enumerate(example_ids):
            subpath = renderings_manager.get_rendering_subpath(
                (cat_id, example_id), view_index)
            vis(zf.open(subpath), rle_data[i, view_index], out_dim)
