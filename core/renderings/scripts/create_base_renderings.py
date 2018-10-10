#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from absl import flags, app
FLAGS = flags.FLAGS

flags.DEFINE_integer('dim', default=256, help='dimension of square renderings')
flags.DEFINE_bool(
    'turntable', default=False, help='render regular angles (default random)')
flags.DEFINE_integer('n_renderings', default=24, help='number of renderings')
flags.DEFINE_bool(
    'verbose', default=True, help='suppress blender output if False')
flags.DEFINE_list(
    'cat', default=None,
    help='category descriptions to render, '
         'comma separated, e.g. chair,sofa,plane')


def main(_):
    from shapenet.core.renderings.renderings_manager import get_base_manager, \
        create_base_manager
    from shapenet.core import to_cat_id
    from shapenet.core.objs import try_extract_models
    cat_ids = [to_cat_id(c) for c in FLAGS.cat]
    for cat_id in cat_ids:
        try_extract_models(cat_id)
    kwargs = dict(
        dim=FLAGS.dim,
        turntable=FLAGS.turntable,
        n_renderings=FLAGS.n_renderings,
    )
    manager = get_base_manager(cat_ids=cat_ids, **kwargs)
    if not os.path.isdir(manager.root_dir):
        create_base_manager()
    manager.render_all(verbose=FLAGS.verbose)


app.run(main)
