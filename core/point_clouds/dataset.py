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

        with mesh_dataset:
            keys = [k for k, v in mesh_dataset.items() if len(v['faces']) > 0]
        mesh_dataset = mesh_dataset.subset(keys)

        return mesh_dataset.map(map_fn)


def _get_point_cloud_dataset(cat_id, n_samples, example_ids=None, mode='r'):
    """
    Get a dataset with point cloud data.

    Args:
        `cat_id`: category id
        `n_samples`: number of points in each cloud
        `example_ids`: If specified, only create data for these examples,
            and return a dataset with only these ids exposed as keys.
            Defaults to all examples in the category.
        `mode`: mode to open the file in. If `a`, data can be deleted or saved.
    """
    manager = PointCloudAutoSavingManager(cat_id, n_samples, example_ids)
    if not os.path.isfile(manager.path):
        dataset = manager.get_saved_dataset()
    else:
        if mode not in ('a', 'r'):
            raise NotImplementedError('mode must be in ("a", "r")')
        dataset = manager.get_saving_dataset(mode=mode)
    if example_ids is not None:
        dataset = dataset.subset(example_ids)
    return dataset


def get_point_cloud_dataset(cat_id, n_samples, example_ids=None, mode='r'):
    from dids.core import BiKeyDataset
    if not isinstance(cat_id, (tuple, list)):
        cat_id = [cat_id]
        example_ids = [example_ids]
    else:
        if example_ids is None:
            example_ids = [None for _ in cat_id]
    datasets = {
        c: _get_point_cloud_dataset(c, n_samples, e, mode)
        for c, e in zip(cat_id, example_ids)}
    return BiKeyDataset(datasets)


class CloudNormalAutoSavingManager(Hdf5AutoSavingManager):
    def __init__(self, cat_id, n_samples, example_ids=None):
        if not isinstance(n_samples, int):
            raise ValueError('n_samples must be an int')
        self._cat_id = cat_id
        self._n_samples = n_samples
        self._example_ids = example_ids

    @property
    def path(self):
        return os.path.join(
            _point_cloud_dir, '_cloud_normals', str(self._n_samples),
            '%s.hdf5' % self._cat_id)

    @property
    def saving_message(self):
        return ('Creating shapenet cloud normal data\n'
                'cat_id: %s\n'
                'n_samples: %d' % (self._cat_id, self._n_samples))

    def get_lazy_dataset(self):
        from shapenet.core.meshes import get_mesh_dataset
        from util3d.mesh.sample import sample_faces_with_normals

        def map_fn(mesh):
            v, f = (np.array(mesh[k]) for k in ('vertices', 'faces'))
            p, n = sample_faces_with_normals(v, f, self._n_samples)
            return dict(points=p, normals=n)

        mesh_dataset = get_mesh_dataset(self._cat_id)
        if self._example_ids is not None:
            mesh_dataset = mesh_dataset.subset(self._example_ids)

        with mesh_dataset:
            keys = [k for k, v in mesh_dataset.items() if len(v['faces']) > 0]
        mesh_dataset = mesh_dataset.subset(keys)

        return mesh_dataset.map(map_fn)


def get_cloud_normal_dataset(cat_id, n_samples, example_ids=None, mode='r'):
    manager = CloudNormalAutoSavingManager(cat_id, n_samples, example_ids)
    if not os.path.isfile(manager.path):
        dataset = manager.get_saved_dataset(mode=mode)
    else:
        dataset = manager.get_saving_dataset(mode=mode)
    if example_ids is not None:
        dataset = dataset.subset(example_ids)
    return dataset
