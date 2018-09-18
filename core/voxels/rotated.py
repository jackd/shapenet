from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np
from .config import VoxelConfig
from . import path


def get_frustrum_transform(fx, fy, near_clip, far_clip, dtype=np.float32):
    depth_range = far_clip - near_clip
    p_22 = -(far_clip + near_clip) / depth_range
    p_23 = -2.0 * (far_clip * near_clip / depth_range)
    return np.array([
        [fx, 0, 0, 0],
        [0, fy, 0, 0],
        [0, 0, p_22, p_23],
        [0, 0, -1, 0]
    ], dtype=dtype)


def look_at(eye, center, world_up):
    # vector_degeneracy_cutoff = 1e-6
    dtype = eye.dtype
    forward = center - eye
    forward_norm = np.linalg.norm(forward, ord=2)
    forward /= forward_norm

    to_side = np.cross(forward, world_up)
    to_side_norm = np.linalg.norm(to_side, ord=2, keepdims=True)

    to_side /= to_side_norm
    cam_up = np.cross(to_side, forward)

    view_rotation = np.stack(
        [to_side, cam_up, -forward],
        axis=0)

    transform = np.empty((4, 4), dtype=dtype)
    transform[:3, :3] = view_rotation
    transform[:3, 3] = np.matmul(view_rotation, -eye)
    transform[3, :3] = 0
    transform[3, 3] = 1
    return transform


def get_frstrum_grid_world_coords(
        fx, fy, near_clip, far_clip, eye_z, theta, shape, linear_z_world=True,
        dtype=np.float32):
    """Get frustrum grid points in world coordinates."""

    frustrum_transform = get_frustrum_transform(fx, fy, near_clip, far_clip)

    nx, ny, nz = shape
    x = 2*(np.array(tuple(range(nx)), dtype=dtype) + 0.5) / nx - 1
    y = 2*(np.array(tuple(range(ny)), dtype=dtype) + 0.5) / ny - 1
    y *= -1  # fixes left/right coordinate frame issues?
    if linear_z_world:
        ze = (np.array(tuple(range(ny)), dtype=dtype) + 0.5) / nz
        ze *= (far_clip - near_clip)
        ze += near_clip
        ze *= -1
        zero = np.zeros_like(ze)
        one = np.ones_like(ze)
        zeht = np.stack([zero, zero, ze, one], axis=0)
        zh = np.matmul(frustrum_transform, zeht).T
        z = zh[..., 2] / zh[..., 3]
    else:
        z = 2*(np.array(tuple(range(ny)), dtype=dtype) + 0.5) / nz - 1
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    xyzh = np.stack([X, Y, Z, np.ones((nx, ny, nz), dtype=dtype)], axis=-1)

    k = np.array([0, 0, 1], dtype=dtype)
    eye = np.array([-np.sin(theta), np.cos(theta), eye_z], dtype=dtype)
    center = np.array([0, 0, 0], dtype=dtype)
    view_transform = look_at(eye, center, k)
    combined_transform = np.matmul(frustrum_transform, view_transform)

    xyzh = np.reshape(xyzh, (-1, 4))
    xyzh_world = np.linalg.solve(combined_transform, xyzh.T).T
    xyzh_world = np.reshape(xyzh_world, (nx, ny, nz, 4))
    xyz_world = xyzh_world[..., :3] / xyzh_world[..., 3:]

    return xyz_world


class FrustrumVoxelConfig(VoxelConfig):
    def __init__(
            self, base_voxel_config, render_config, view_index, shape):
        self._base_config = base_voxel_config
        self._view_index = view_index
        self._theta = np.deg2rad(render_config.view_angle(view_index))
        scale = render_config.scale
        if scale is None:
            scale = 1
        self._eye_z = 0.6
        D = np.sqrt(self._eye_z**2 + 1)
        self._near_clip = D - 0.5*scale
        self._far_clip = self._near_clip + scale
        self._shape = shape
        self._view_index = view_index
        self._shape = tuple(shape)
        assert(
            len(self._shape) == 3 and
            all(isinstance(s, int) for s in self._shape))
        self._voxel_id = '%s_%s%d_%s' % (
                base_voxel_config.voxel_id, render_config.config_id,
                view_index, '-'.join(str(s) for s in shape))
        h, w = render_config.shape
        # fx = 35 / 32
        fx = 35 / (32 / 2)
        fy = fx * h / w

        self._fx = fx
        self._fy = fy

    @property
    def shape(self):
        return self._shape

    @property
    def voxel_id(self):
        return self._voxel_id

    @property
    def root_dir(self):
        dir = os.path.join(path.data_dir, 'rotated', self.voxel_id)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        return dir

    def transformer(self):
        world_coords = get_frstrum_grid_world_coords(
                self._fx, self._fy, self._near_clip, self._far_clip,
                self._eye_z, self._theta, self._shape,
                linear_z_world=True)
        voxel_dim = self._base_config.voxel_dim
        voxel_coords = (world_coords + 0.5) * voxel_dim
        voxel_coords = np.floor(voxel_coords).astype(np.int32)
        inside = np.all(
            np.logical_and(voxel_coords >= 0, voxel_coords < voxel_dim),
            axis=-1)
        outside = np.logical_not(inside)
        voxel_coords[outside] = 0

        coords_flat = np.reshape(voxel_coords, (-1, 3))
        i, j, k = coords_flat.T
        shape = self.shape

        def f(voxels):
            data = voxels.gather((i, j, k))
            # data = voxels.gather((i, j, k))
            # data = voxels.gather((i, j, k), fix_coords=True)
            # data = voxels.dense_data()[i, j, k]
            data = np.reshape(data, shape)
            data[outside] = 0
            return data

        return f

    def create_voxel_data(self, cat_id, example_ids=None, overwrite=False):
        from progress.bar import IncrementalBar
        from util3d.voxel.binvox import DenseVoxels
        transformer = self.transformer()
        with self._base_config.get_dataset(cat_id, 'r') as base:
            if example_ids is None:
                example_ids = tuple(base.keys())
            bar = IncrementalBar(max=len(example_ids))
            for example_id in example_ids:
                bar.next()
                path = self.get_binvox_path(cat_id, example_id)
                if os.path.isfile(path):
                    if overwrite:
                        os.remove(path)
                    else:
                        continue
                out = DenseVoxels(transformer(base[example_id]))
                out.save(path)
            bar.finish()
