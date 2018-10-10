#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

flags.DEFINE_integer('dim', default=256, help='dimension of square renderings')
flags.DEFINE_bool('turntable', default=False, help='if True, renderings')
flags.DEFINE_integer('n_renderings', default=24, help='number of renderings')
flags.DEFINE_string('path', default=None, help='(optional) path to save')
flags.DEFINE_list(
    'cat', default=None, help='cat(s), either ids of descriptors')
flags.DEFINE_boolean(
    'full', default=False, help='compress all images (True), or just base')
flags.DEFINE_string(
    'format', default='tar', help='compression format, one of ["zip", "tar"]')
flags.DEFINE_boolean('check', default=False, help='If True, just runs a check')


def main(_):
    from shapenet.core.renderings.archive_manager import get_archive_manager
    from shapenet.core.renderings.renderings_manager import get_base_manager

    rend_manager = get_base_manager(
        dim=FLAGS.dim, turntable=FLAGS.turntable,
        n_renderings=FLAGS.n_renderings)
    if FLAGS.cat is None:
        from shapenet.r2n2 import get_cat_ids
        cats = get_cat_ids()
    else:
        cats = FLAGS.cat
    format = FLAGS.format
    mode = 'r' if FLAGS.check else 'a'
    for cat in cats:
        archive_manager = get_archive_manager(
            rend_manager, cat, base_only=not FLAGS.full,
            format=format, mode=mode)
        with archive_manager.archive:
            if FLAGS.check:
                archive_manager.check()
            else:
                archive_manager.add()


app.run(main)
