#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

flags.DEFINE_integer('dim', default=128, help='dimension of square renderings')
flags.DEFINE_bool('turntable', default=False, help='if True, renderings')
flags.DEFINE_integer('n_renderings', default=24, help='number of renderings')
flags.DEFINE_string(
    'compression', default='lzf', help='hdf5 compression format')
flags.DEFINE_string('path', default=None, help='path to save')


def main(_):
    from shapenet.core.renderings.manager import get_base_manager
    from shapenet.core.renderings.hdf5 import create_camera_positions
    manager = get_base_manager(
        dim=FLAGS.dim, turntable=FLAGS.turntable,
        n_renderings=FLAGS.n_renderings)
    create_camera_positions(
        manager, cats=None, compression=FLAGS.compression, path=FLAGS.path)


app.run(main)
