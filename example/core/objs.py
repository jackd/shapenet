
from shapenet.core import cat_desc_to_id
from shapenet.core.objs import get_obj_file_dataset
from mayavi import mlab
from util3d.mayavi_vis import vis_mesh
from util3d.mesh.obj_io import parse_obj_file

cat_desc = 'plane'
cat_id = cat_desc_to_id(cat_desc)


def map_fn(f):
    return parse_obj_file(f)[:2]


dataset = get_obj_file_dataset(cat_id).map(map_fn)

with dataset:
    for k, (vertices, faces) in dataset.items():
        print(k)
        vis_mesh(vertices, faces, axis_order='xzy')
        mlab.show()
