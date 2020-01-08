#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

flags.DEFINE_integer('dim', default=256, help='dimension of square renderings')
flags.DEFINE_bool('turntable', default=False, help='if True, renderings')
flags.DEFINE_integer('n_views', default=24, help='number of views')
flags.DEFINE_integer('voxel_dim', default=32, help='output voxel dimension')
flags.DEFINE_integer(
    'src_voxel_dim', default=256, help='input voxel dimension')
flags.DEFINE_list(
    'cat', default=None, help='category ids/descriptors, comma separated')


def main(_):
    from progress.bar import IncrementalBar
    import numpy as np
    from shapenet.core import to_cat_id
    from shapenet.core.renderings.renderings_manager import get_base_manager
    from shapenet.core.frustrum_voxels import get_frustrum_voxels_data
    from shapenet.core.frustrum_voxels import GROUP_KEY
    from shapenet.core.voxels.config import get_config
    from util3d.voxel import rle
    voxel_config = get_config(
        FLAGS.src_voxel_dim, alt=False).filled('orthographic')
    manager = get_base_manager(
        dim=FLAGS.dim, turntable=FLAGS.turntable, n_views=FLAGS.n_views)

    cats = FLAGS.cat
    if cats is None:
        from shapenet.r2n2 import get_cat_ids
        cats = get_cat_ids()

    expected_length = FLAGS.voxel_dim**3

    for ci, cat in enumerate(cats):
        # if ci >= 3:
        #     continue
        cat_id = to_cat_id(cat)
        print('Checking cat %s: %d / %d' % (cat_id, ci+1, len(cats)))
        with get_frustrum_voxels_data(
                manager.root_dir, voxel_config, FLAGS.voxel_dim,
                cat_id) as root:
            data = root[GROUP_KEY]
            ne, nr = data.shape[:2]
            bar = IncrementalBar(max=ne)
            for i in range(ne):
                bar.next()
                di = np.array(data[i])
                for j in range(nr):
                    actual_length = rle.length(di[j])
                    # actual_length = len(rle.rle_to_dense(di[j]))
                    if actual_length != expected_length:
                        raise ValueError(
                            'Incorrect length at %s, %d, %d\n'
                            'Expected %d, got %d'
                            % (cat_id, i, j, expected_length, actual_length))
            bar.finish()


app.run(main)
