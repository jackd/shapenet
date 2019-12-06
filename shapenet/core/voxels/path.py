from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from ..path import get_data_dir

data_dir = get_data_dir('voxels')
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)


def get_binvox_subpath(cat_id, example_id=None):
    if example_id is None:
        return cat_id
    return os.path.join(cat_id, '%s.binvox' % example_id)


def get_binvox_dir(voxel_id):
    return os.path.join(data_dir, voxel_id)
