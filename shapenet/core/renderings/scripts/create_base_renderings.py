#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

flags.DEFINE_integer('dim', default=128, help='dimension of square renderings')
flags.DEFINE_bool(
    'turntable', default=False, help='render regular angles (default random)')
flags.DEFINE_integer('n_views', default=24, help='number of views to render')
flags.DEFINE_bool(
    'verbose', default=True, help='suppress blender output if False')
flags.DEFINE_list(
    'cat', default=None,
    help='category descriptions to render, '
         'comma separated, e.g. chair,sofa,plane')


def main(_):
    from shapenet.core.renderings.renderings_manager import get_base_manager
    from shapenet.core import to_cat_id
    from shapenet.core.objs import try_extract_models
    cat_ids = [to_cat_id(c) for c in FLAGS.cat]
    for cat_id in cat_ids:
        try_extract_models(cat_id)

    manager = get_base_manager(
        dim=FLAGS.dim,
        turntable=FLAGS.turntable,
        n_views=FLAGS.n_views,
    )
    manager.render_all(cat_ids=cat_ids, verbose=FLAGS.verbose)


app.run(main)
