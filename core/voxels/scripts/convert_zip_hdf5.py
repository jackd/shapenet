#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from shapenet.core import get_cat_ids
from shapenet.core.voxels import VoxelConfig
from shapenet.core.voxels.filled import FillAlg
import zipfile

delete_src = True
cat_ids = get_cat_ids()


def needs_conversion(config):
    for cat_id in cat_ids:
        if os.path.isfile(config.get_zip_path(cat_id)) \
                and not os.path.isfile(config.get_hdf5_path(cat_id)):
            yield cat_id


configs = []
for dim in (20, 32, 64, 128, 256):
    base = VoxelConfig(dim)
    configs.append(base)
    for alg in (FillAlg.BASE, FillAlg.ORTHOGRAPHIC):
        configs.append(base.filled(alg))

pairs = []
for config in configs:
    for cat_id in needs_conversion(config):
        pairs.append((config, cat_id))

n = len(pairs)
print('Converting %d pairs' % n)
for i, (config, cat_id) in enumerate(pairs):
    print('%s - %s: %d / %d' % (config.voxel_id, cat_id, i+1, n))
    try:
        config.create_hdf5_data_from_zip(cat_id, delete_src=delete_src)
    except zipfile.BadZipfile:
        path = config.get_zip_path(cat_id)
        print('Bad zip file at %s: removing' % path)
        os.remove(path)
    except Exception, KeyboardInterrupt:
        if os.path.isfile(config.get_hdf5_path(cat_id)):
            os.remove(config.get_hdf5_path(cat_id))
        print('Error converting %s' % config.get_zip_path(cat_id))
        raise
