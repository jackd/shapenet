#!/usr/bin/python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
from shapenet.r2n2.hdf5 import Hdf5Manager, get_cat_ids
from shapenet.r2n2.split import split_indices

cat_id = random.sample(get_cat_ids(), 1)[0]
# cat_id = '03691459'
view_index = 0


def vis(vox, image, meta):
    from mayavi import mlab
    from util3d.mayavi_vis import vis_voxels
    print(meta)
    image.resize((137*4,)*2).show()
    mlab.figure()
    vis_voxels(vox, color=(0, 0, 1), scale_factor=0.5, axis_order='xyz')
    mlab.show()


print('Opening manager...')
with Hdf5Manager(cat_id) as m:
    print('Getting example_ids...')
    example_ids = m.get_example_ids()
    print('Getting split indices')
    indices = split_indices(example_ids, 'train')
    print(indices[:10])
    for index in indices:
        print('Loading data...')
        vox = m.get_voxels(index).dense_data()
        image = m.get_rendering(index, view_index)
        meta = m.get_meta(index, view_index)
        print('Visualizing...')
        vis(vox, image, meta)
