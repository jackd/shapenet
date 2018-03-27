from mayavi import mlab
from shapenet.core.voxels.config import VoxelConfig
from shapenet.core import cat_desc_to_id, get_example_ids
from util3d.mayavi_vis import vis_voxels

cat_desc = 'plane'
cat_id = cat_desc_to_id(cat_desc)
example_ids = get_example_ids(cat_id)

config = VoxelConfig()
with config.get_dataset(cat_id) as dataset:
    for example_id in example_ids:
        voxels = dataset[example_id]
        vis_voxels(voxels.dense_data(), color=(0, 0, 1))
        mlab.show()
