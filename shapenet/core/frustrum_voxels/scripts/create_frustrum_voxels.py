#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

flags.DEFINE_integer('dim', default=256, help='dimension of square renderings')
flags.DEFINE_bool(
    'turntable', default=False,
    help='if True, views are based on equal rotation about z axis')
flags.DEFINE_integer('n_views', default=24, help='number of views')
flags.DEFINE_integer('voxel_dim', default=32, help='output voxel dimension')
flags.DEFINE_integer(
    'src_voxel_dim', default=None, help='input voxel dimension')
flags.DEFINE_list(
    'cat', default=None, help='category ids/descriptors, comma separated')
flags.DEFINE_bool('temp_only', default=False, help='If True, does not squeeze')
flags.DEFINE_string(
    'compression', default='lzf', help='compression for encoded data')
flags.DEFINE_string(
    'fill_alg', default='orthographic',
    help='fill algorithm for base voxel grid.')


def main(_):
    from shapenet.core import to_cat_id
    from shapenet.core.renderings.renderings_manager import get_base_manager
    from shapenet.core.frustrum_voxels import create_frustrum_voxels
    from shapenet.core.frustrum_voxels import create_temp_frustrum_voxels
    from shapenet.core.voxels.config import get_config
    if FLAGS.src_voxel_dim is None:
        FLAGS.src_voxel_dim = FLAGS.voxel_dim

    voxel_config = get_config(
        FLAGS.src_voxel_dim, alt=False).filled(FLAGS.fill_alg)
    manager = get_base_manager(
        dim=FLAGS.dim, turntable=FLAGS.turntable,
        n_views=FLAGS.n_views)

    cats = FLAGS.cat
    if cats is None:
        from shapenet.r2n2 import get_cat_ids
        cats = get_cat_ids()

    for cat in cats:
        cat_id = to_cat_id(cat)
        args = manager, voxel_config, FLAGS.voxel_dim, cat_id
        if FLAGS.temp_only:
            create_temp_frustrum_voxels(*args, compression=FLAGS.compression)
        else:
            create_frustrum_voxels(*args, compression=FLAGS.compression)


app.run(main)
