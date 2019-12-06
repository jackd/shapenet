#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

flags.DEFINE_integer('dim', default=128, help='dimension of square renderings')
flags.DEFINE_bool(
    'turntable', default=False, help='render regular angles (default random)')
flags.DEFINE_integer('n_views', default=24, help='number of views')
flags.DEFINE_list(
    'cat', default=None,
    help='category descriptions to render, '
         'comma separated, e.g. chair,sofa,plane')


def main(_):
    from shapenet.core.renderings.renderings_manager import get_base_manager
    from shapenet.core import cat_desc_to_id
    from shapenet.core import cat_id_to_desc
    cat = FLAGS.cat
    if cat is None or len(cat) == 0:
        from shapenet.r2n2 import get_cat_ids
        cat_ids = get_cat_ids()
    else:
        cat_ids = [cat_desc_to_id(c) for c in FLAGS.cat]

    print('Required renderings:')
    for cat_id in cat_ids:
        manager = get_base_manager(
            dim=FLAGS.dim,
            turntable=FLAGS.turntable,
            n_views=FLAGS.n_views,
        )
        n = len(tuple(manager.needs_rendering_keys(cat_ids=[cat_id])))
        n_total = len(tuple(manager.view_manager.keys(cat_ids=[cat_id])))
        cat = cat_id_to_desc(cat_id)
        print('%s: %s\n  %d / %d' % (cat_id, cat, n, n_total))


app.run(main)
