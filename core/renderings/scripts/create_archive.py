#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

flags.DEFINE_integer('dim', default=128, help='dimension of square renderings')
flags.DEFINE_bool('turntable', default=False, help='if True, renderings')
flags.DEFINE_integer('n_renderings', default=24, help='number of renderings')
flags.DEFINE_string('path', default=None, help='(optional) path to save')
flags.DEFINE_list(
    'cat', default=None, help='cat(s), either ids of descriptors')
flags.DEFINE_boolean(
    'full', default=False, help='compress all images (True), or just base')
flags.DEFINE_string(
    'format', default='tar', help='compression format, one of ["zip", "tar"]')


def main(_):
    from shapenet.core.renderings.manager import get_base_manager

    manager = get_base_manager(
        dim=FLAGS.dim, turntable=FLAGS.turntable,
        n_renderings=FLAGS.n_renderings)
    if FLAGS.cat is None:
        raise ValueError('Please specify at least one cat')
    format = FLAGS.format
    if format == 'zip':
        from shapenet.core.renderings.rzip import add_renderings
        for cat in FLAGS.cat:
            add_renderings(
                manager, cat=cat, path=FLAGS.path, base_only=not FLAGS.full)
    elif format == 'tar':
        from shapenet.core.renderings.rtar import add_renderings
        for cat in FLAGS.cat:
            add_renderings(
                manager, cat=cat, path=FLAGS.path, base_only=not FLAGS.full)


app.run(main)
