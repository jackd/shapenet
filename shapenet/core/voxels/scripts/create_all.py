#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from shapenet.r2n2 import get_cat_ids
from shapenet.core.voxels.datasets import get_manager, convert
from shapenet.core.voxels import get_config

cat_ids = get_cat_ids()
voxel_dims = (32, 64, 128, 256)
n_configs = 2
n = len(cat_ids) * len(voxel_dims) * n_configs
i = 1
for voxel_dim in voxel_dims:
    for config in (
            get_config(voxel_dim).filled('orthographic'),
            get_config(voxel_dim, alt=True),
            ):
        for cat_id in cat_ids:
            dst = get_manager(
                config, cat_id, key='brle', compression='lzf', pad=True)
            src_kwargs = dict(key='file')
            print('Converting %d / %d' % (i, n))
            convert(dst, overwrite=False, delete_src=False, **src_kwargs)
            i += 1
