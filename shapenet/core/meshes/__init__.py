import os
import dids.file_io.hdf5 as dh
from ..path import get_data_dir


_meshes_dir = get_data_dir('meshes')


class _MeshAutoSavingManager(dh.Hdf5AutoSavingManager):
    def __init__(self, cat_id):
        self.cat_id = cat_id

    @property
    def path(self):
        return os.path.join(_meshes_dir, '%s.hdf5' % self.cat_id)

    @property
    def saving_message(self):
        return 'Parsing mesh data for cat_id %s' % self.cat_id

    def get_lazy_dataset(self):
        from shapenet.core.objs import get_obj_file_dataset
        from util3d.mesh.obj_io import parse_obj_file

        def map_fn(f):
            vertices, faces = parse_obj_file(f)[:2]
            return dict(vertices=vertices, faces=faces)

        return get_obj_file_dataset(self.cat_id).map(map_fn)


def remove_empty_meshes(cat_id):
    from shapenet.core.meshes import get_mesh_dataset
    to_remove = []
    with get_mesh_dataset(cat_id, mode='a') as ds:
        for example_id, mesh in ds.items():
            if len(mesh['faces']) == 0:
                to_remove.append(example_id)
        for t in to_remove:
            del ds[t]
    return to_remove


def generate_mesh_data(cat_id, overwrite=False):
    _MeshAutoSavingManager(cat_id).save_all(overwrite=overwrite)
    remove_empty_meshes(cat_id)


def get_mesh_dataset(cat_id, mode='r'):
    manager = _MeshAutoSavingManager(cat_id)
    if not os.path.isfile(manager.path):
        manager.save_all()
    return manager.get_saving_dataset(mode)


# __all__ = [
#     get_mesh_dataset,
#     generate_mesh_data,
# ]
