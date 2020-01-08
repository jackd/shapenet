#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import dids
from shapenet.core.point_clouds import get_point_cloud_dataset
from shapenet.core.meshes import get_mesh_dataset
from shapenet.core import cat_desc_to_id, get_test_train_split

cat_desc = 'plane'
cat_id = cat_desc_to_id(cat_desc)

cloud_ds = get_point_cloud_dataset(cat_id, 1024)
mesh_ds = get_mesh_dataset(cat_id)

zipped_ds = dids.Dataset.zip(mesh_ds, cloud_ds)


def vis(mesh, cloud):
    import numpy as np
    from util3d.mayavi_vis import vis_mesh, vis_point_cloud
    from mayavi import mlab
    vertices, faces = (np.array(mesh[k]) for k in ('vertices', 'faces'))
    vis_mesh(vertices, faces, color=(0, 0, 1), axis_order='xzy')
    vis_point_cloud(
        np.array(cloud), color=(0, 1, 0), scale_factor=0.01, axis_order='xzy')
    mlab.show()


test_train_split = get_test_train_split()[cat_id]
train_keys = test_train_split['train']
test_keys = test_train_split['test']
val_keys = test_train_split['val']

with zipped_ds:
    print(len(zipped_ds))
    train_ds = zipped_ds.subset(train_keys)
    test_ds = zipped_ds.subset(test_keys)
    val_ds = zipped_ds.subset(val_keys)
    print('n train: %d, n valid train: %d' % (len(train_keys), len(train_ds)))
    print('n test: %d, n valid test: %d' % (len(test_keys), len(test_ds)))
    print('n val: %d, n valid val: %d' % (len(val_keys), len(val_ds)))

    for example_id in train_ds.keys():
        print('train dataset, example_id: %s' % example_id)
        mesh, cloud = train_ds[example_id]
        break
    vis(mesh, cloud)

    for example_id in test_ds.keys():
        print('test dataset, example_id: %s' % example_id)
        mesh, cloud = test_ds[example_id]
        break
    vis(mesh, cloud)

    for example_id in val_ds.keys():
        print('val dataset, example_id: %s' % example_id)
        mesh, cloud = val_ds[example_id]
        break
    vis(mesh, cloud)
