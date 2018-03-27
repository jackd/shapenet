import numpy as np
from mayavi import mlab
from util3d.mayavi_vis import vis_point_cloud
from shapenet.core.point_clouds import get_point_cloud_dataset
from shapenet.core import cat_desc_to_id

cat_desc = 'plane'
n_points = 16384
cat_id = cat_desc_to_id(cat_desc)

with get_point_cloud_dataset(cat_id, n_points) as dataset:
    for example_id in dataset:
        cloud = np.array(dataset[example_id])
        vis_point_cloud(
            cloud, axis_order='xzy', color=(0, 0, 1), scale_factor=0.002)
        mlab.show()
