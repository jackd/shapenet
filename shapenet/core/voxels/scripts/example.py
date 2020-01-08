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

flags.DEFINE_string(
    'cat', default=None, help='catergory to create (ID or descriptor)')
flags.DEFINE_list(
    'example_id', default=None,
    help='example id(s) to create base for. Defaults to all')


def main(_):
    from shapenet.core.voxels.config import get_config
    from shapenet.core import to_cat_id
    from shapenet.core import get_example_ids
    config = get_config(FLAGS.voxel_dim, alt=FLAGS.alt)
    fill = FLAGS.fill
    if fill is not None:
        config = config.filled(fill)
    if FLAGS.cat is None:
        raise ValueError('Must provide at least one cat to convert.')
    if FLAGS.fill is not None:
        config = config.filled(FLAGS.fill)
    cat_id = to_cat_id(FLAGS.cat)
    example_ids = FLAGS.example_id
    if example_ids is None:
        example_ids = get_example_ids(cat_id)
    config.create_voxel_data(cat_id, example_ids)


app.run(main)
