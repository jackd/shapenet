#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

flags.DEFINE_integer('dim', default=256, help='dimension of square renderings')
flags.DEFINE_bool('turntable', default=False, help='if True, renderings')
flags.DEFINE_integer('n_renderings', default=24, help='number of renderings')


def main(_):
    from shapenet.core.renderings.renderings_manager import create_base_manager
    create_base_manager(
        dim=FLAGS.dim, turntable=FLAGS.turntable,
        n_renderings=FLAGS.n_renderings)


app.run(main)
