from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from .manager import WritableViewManager
from .. import get_example_ids


class H5ViewManager(WritableViewManager):
    def __init__(self, base_group):
        self._base_group = base_group
        self._indices = {}

    def get_example_indices(self, cat_id):
        if cat_id not in self._indices:
            example_ids = self.get_example_ids(cat_id)
            indices = {k: i for i, k in enumerate(example_ids)}
            self._indices[cat_id] = indices
        return self._indices[cat_id]

    def _get_view_params(self):
        return self._base_group.require_group('view_params').attrs

    def get_view_params(self):
        return dict(**self._get_view_params())

    def get_camera_positions(self, cat_id, example_id):
        return self.get_camera_positions_from_index(
            cat_id, self.get_example_indices(cat_id)[example_id])

    def get_camera_positions_from_index(self, cat_id, example_index):
        return np.array(self.camera_positions_group[cat_id][example_index])

    @property
    def camera_positions_group(self):
        return self._base_group.require_group('camera_positions')

    def set_view_params(self, **params):
        attrs = self._get_view_params()
        for k, v in params.items():
            attrs[k] = v

    def set_camera_positions(self, cat_id, example_id, value):
        example_indices = self.get_example_indices(cat_id)
        n = len(example_indices)
        example_index = example_indices[example_id]
        dataset = self.camera_positions_group.require_dataset(
                cat_id, shape=(n, self.get_view_params()['n_views'], 3),
                dtype=np.float32, exact=True)
        dataset[example_index] = value

    def get_example_ids(self, cat_id):
        return get_example_ids(cat_id)

    def get_cat_ids(self):
        return self._base_group.require_group('camera_positions').keys()


def get_base_h5_manager_path(turntable=False, n_views=24):
    import os
    from ..path import get_data_dir
    from .base import get_base_id
    return os.path.join(
        get_data_dir('views'), '%s.h5' % get_base_id(turntable, n_views))


def get_base_h5_manager(turntable=False, n_views=24):
    import os
    import h5py
    from .lazy import get_base_lazy_manager
    data_path = get_base_h5_manager_path(
        turntable, n_views)
    if os.path.isfile(data_path):
        fp = h5py.File(data_path, mode='r')
        return H5ViewManager(fp)
    else:
        try:
            with h5py.File(data_path, 'w') as fp:
                manager = H5ViewManager(fp)
                manager.copy_from(get_base_lazy_manager(turntable, n_views))
            return H5ViewManager(h5py.File(data_path, mode='r'))
        except (Exception, KeyboardInterrupt):
            os.remove(data_path)
            raise
