from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .manager import ViewManager


class LazyViewManager(ViewManager):
    def __init__(
            self, view_params, cat_ids, example_ids_fn, camera_pos_fn):
        self._view_params = view_params
        self._cat_ids = tuple(cat_ids)
        self._example_ids_fn = example_ids_fn
        self._camera_pos_fn = camera_pos_fn

    def get_view_params(self):
        return self._view_params.copy()

    def get_camera_positions(self, cat_id, example_id):
        return self._camera_pos_fn(cat_id, example_id)

    def get_example_ids(self, cat_id):
        return self._example_ids_fn(cat_id)

    def get_cat_ids(self):
        return self._cat_ids


def get_base_lazy_manager(turntable=False, n_views=24, seed=0):
    import numpy as np
    from ...r2n2 import get_cat_ids
    from .. import get_example_ids
    from .base import get_base_id
    cat_ids = get_cat_ids()
    dist = 1.166  # sqrt(1 + 0.6**2) - looked good in experiments

    def polar_to_cartesian(dist, theta, phi):
        z = np.cos(phi)
        s = np.sin(phi)
        x = s * np.cos(theta)
        y = s * np.sin(theta)
        return np.stack((x, y, z), axis=-1) * dist

    if turntable:
        def get_camera_pos():
            theta = np.deg2rad(np.linspace(0, 360, n_views+1)[:-1])
            phi = np.deg2rad(60.0) * np.ones_like(theta)
            return polar_to_cartesian(dist, theta, phi).astype(np.float32)
    else:
        np.random.seed(seed)

        def get_camera_pos():
            size = (n_views,)
            theta = np.deg2rad(np.random.uniform(0, 360, size=size))
            phi = np.deg2rad(90 - np.random.uniform(25, 30, size=size))
            return polar_to_cartesian(dist, theta, phi).astype(np.float32)

    view_params = dict(
        depth_scale=1.4,
        scale=1,
        n_views=24,
        f=32 / 35,
        view_id=get_base_id(turntable=turntable, n_views=n_views)
    )

    return LazyViewManager(
        view_params, cat_ids, get_example_ids,
        lambda cat_id, example_id: get_camera_pos())
