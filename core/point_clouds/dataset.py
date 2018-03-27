import os
import numpy as np
from dids.file_io.hdf5 import Hdf5AutoSavingManager

_point_cloud_dir = os.path.realpath(os.path.dirname(__file__))


class PointCloudAutoSavingManager(Hdf5AutoSavingManager):
    def __init__(self, cat_id, n_samples, example_ids=None):
        if not isinstance(n_samples, int):
            raise ValueError('n_samples must be an int')
        self._cat_id = cat_id
        self._n_samples = n_samples
        self._example_ids = example_ids

    @property
    def path(self):
        return os.path.join(
            _point_cloud_dir, '_point_clouds', str(self._n_samples),
            '%s.hdf5' % self._cat_id)

    @property
    def saving_message(self):
        return ('Creating shapenet point cloud\n'
                'cat_id: %s\n'
                'n_samples: %d' % (self._cat_id, self._n_samples))

    def get_lazy_dataset(self):
        from shapenet.core.meshes import get_mesh_dataset
        from util3d.mesh.sample import sample_faces

        def map_fn(mesh):
            v, f = (np.array(mesh[k]) for k in ('vertices', 'faces'))
            return sample_faces(v, f, self._n_samples)

        mesh_dataset = get_mesh_dataset(self._cat_id)
        if self._example_ids is not None:
            mesh_dataset = mesh_dataset.subset(self._example_ids)

        return mesh_dataset.map(map_fn)


def get_point_cloud_dataset(cat_id, n_samples, example_ids=None):
    manager = PointCloudAutoSavingManager(cat_id, n_samples, example_ids)
    if not os.path.isfile(manager.path):
        return manager.get_saved_dataset()
    else:
        return manager.get_saving_dataset()
