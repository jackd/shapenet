#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

# VoxelConfig args
flags.DEFINE_integer('voxel_dim', default=32, help='voxel dimension')
flags.DEFINE_boolean(
    'alt', default=False, help='use alternative base VoxelConfig')
flags.DEFINE_string('fill', default=None, help='optional fill algorithm')
flags.DEFINE_list(
    'cat', default=None, help='catergory(s) to create (ID or descriptor)')


def main(_):
    from shapenet.core.voxels.config import get_config
    from shapenet.core import to_cat_id
    from shapenet.r2n2 import get_cat_ids
    config = get_config(FLAGS.voxel_dim, alt=FLAGS.alt)
    fill = FLAGS.fill
    if fill is not None:
        config = config.filled(fill)
    if FLAGS.cat is None:
        cat_ids = get_cat_ids()
    else:
        cat_ids = [to_cat_id(c) for c in FLAGS.cat]
    if FLAGS.fill is not None:
        config = config.filled(FLAGS.fill)
    for cat_id in cat_ids:
        config.create_voxel_data(cat_id)


app.run(main)
