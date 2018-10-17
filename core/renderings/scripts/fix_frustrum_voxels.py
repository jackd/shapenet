#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from shapenet.core.renderings.frustrum_voxels import fix
from shapenet.core.renderings.renderings_manager import get_base_manager
from shapenet.core.voxels.config import get_config

# found error with this guy - not sure why...
cat_id, example_index, view_index = '02933112', 1571, 11

out_dim = 128
src_dim = 256
image_dim = 256
n_renderings = 24

manager = get_base_manager(
    dim=image_dim, turntable=False, n_renderings=n_renderings)
voxel_config = get_config(src_dim, alt=False).filled('orthographic')

fix(manager, voxel_config, out_dim, cat_id, example_index, view_index)
