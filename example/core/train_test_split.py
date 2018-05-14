import dids
import random
from shapenet.core.point_clouds import get_point_cloud_dataset
from shapenet.core.meshes import get_mesh_dataset
from shapenet.core import cat_desc_to_id

cat_desc = 'plane'
cat_id = cat_desc_to_id(cat_desc)

cloud_ds = get_point_cloud_dataset(cat_id, 1024)
mesh_ds = get_mesh_dataset(cat_id)

zipped_ds = dids.Dataset.zip(mesh_ds, cloud_ds)
train_frac = 0.9


def vis(mesh, cloud):
    import numpy as np
    from util3d.mayavi_vis import vis_mesh, vis_point_cloud
    from mayavi import mlab
    vertices, faces = (np.array(mesh[k]) for k in ('vertices', 'faces'))
    vis_mesh(vertices, faces, color=(0, 0, 1), axis_order='xzy')
    vis_point_cloud(
        np.array(cloud), color=(0, 1, 0), scale_factor=0.01, axis_order='xzy')
    mlab.show()


with zipped_ds:
    keys = list(zipped_ds.keys())
    keys.sort()
    random.seed(0)  # for reproducibility
    random.shuffle(keys)
    n = int(train_frac * len(keys))
    train_keys = keys[:n]
    test_keys = keys[n:]

    train_ds = zipped_ds.subset(train_keys)
    test_ds = zipped_ds.subset(test_keys)

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
