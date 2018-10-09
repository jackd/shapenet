from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np
import h5py
from .hdf5 import get_camera_positions
from ..voxels.datasets import get_manager

from util3d.transform.frustrum import voxel_values_to_frustrum
from util3d.transform.nonhom import get_eye_to_world_transform
from util3d.voxel.binvox import DenseVoxels, RleVoxels


compression = 'lzf'
f = 32 / 35


def _make_dir(filename):
    folder = os.path.dirname(filename)
    if not os.path.isdir(folder):
        os.makedirs(folder)


def convert(vox, eye, ray_shape):
    dense_data = vox.dense_data()
    dense_data = dense_data[:, -1::-1]
    n = np.linalg.norm(eye)
    R, t = get_eye_to_world_transform(eye)
    z_near = n - 0.5
    z_far = z_near + 1

    frust, inside = voxel_values_to_frustrum(
        dense_data, R, t, f, z_near, z_far, ray_shape,
        include_corners=False)
    frust[np.logical_not(inside)] = 0
    frust = frust[:, -1::-1]
    return DenseVoxels(frust)


def _get_frustrum_voxels_path(
        render_manager, voxel_config, out_dim, cat_id, temp):
    fn = ('temp_%s.hdf5' % cat_id) if temp else ('%s.hdf5' % cat_id)
    return os.path.join(
        render_manager.root_dir, 'frustrum_voxels', voxel_config.voxel_id,
        'v%03d' % out_dim, fn)


def get_frustrum_voxels_path(
        render_manager, voxel_config, out_dim, cat_id):
    return _get_frustrum_voxels_path(
        render_manager, voxel_config, out_dim, cat_id, temp=False)


def create_temp_frustrum_voxels(
        render_manager, voxel_config, out_dim, cat_id):
    from progress.bar import IncrementalBar
    n_renderings = render_manager.get_render_params()['n_renderings']
    in_dims = (voxel_config.voxel_dim,) * 3
    ray_shape = (out_dim,) * 3
    with get_camera_positions(render_manager) as camera_pos:
        eye_group = camera_pos[cat_id]
        n0 = len(eye_group)
        dst_path = _get_frustrum_voxels_path(
                render_manager, voxel_config, out_dim, cat_id, temp=True)
        _make_dir(dst_path)
        with h5py.File(dst_path, 'a') as vox_dst:
            attrs = vox_dst.attrs
            prog = attrs.get('prog', 0)
            if prog == n0:
                return

            attrs.setdefault('n_renderings', n_renderings)
            max_len = attrs.setdefault('max_len', 0)

            vox_manager = get_manager(
                voxel_config, cat_id, key='rle',
                compression=compression, shape_key='pad')
            if not vox_manager.has_dataset():
                raise RuntimeError('No dataset')
            with h5py.File(vox_manager.path, 'r') as vox_src:
                rle_src = vox_src['rle-pad-lzf_data']

                n, m = rle_src.shape
                max_max_len = m * 3
                assert(n == n0)

                print('Creating temp rle frustrum voxel data at %s' % dst_path)
                rle_dst = vox_dst.require_dataset(
                    'rle-pad-lzf_data', shape=(n, n_renderings, max_max_len),
                    dtype=np.uint8, compression=compression)
                bar = IncrementalBar(max=n-prog)
                for i in range(prog, n):
                    bar.next()
                    vox = RleVoxels(np.array(rle_src[i]), in_dims)
                    eye = eye_group[i]
                    for j in range(n_renderings):
                        out = convert(vox, eye[j], ray_shape)
                        data = out.rle_data()
                        dlen = len(data)
                        if dlen > max_len:
                            attrs['max_len'] = dlen
                            max_len = dlen
                            if dlen > max_max_len:
                                raise ValueError(
                                    'max_max_len exceeded. %d > %d'
                                    % (dlen, max_max_len))
                        rle_dst[i, j, :dlen] = data
                    attrs['prog'] = i
                bar.finish()


def create_frustrum_voxels(render_manager, voxel_config, out_dim, cat_id):
    kwargs = dict(
        render_manager=render_manager, voxel_config=voxel_config,
        out_dim=out_dim, cat_id=cat_id)
    dst_path = _get_frustrum_voxels_path(temp=False, **kwargs)
    if os.path.isfile(dst_path):
        print('Already present.')
        return
    create_temp_frustrum_voxels(**kwargs)
    src_path = _get_frustrum_voxels_path(temp=True, **kwargs)

    print('Shrinking data to fit.')
    with h5py.File(src_path, 'r') as src:
        max_len = src.attrs['max_len']
        src_group = src['rle-pad-lzf_data']
        _make_dir(dst_path)
        with h5py.File(dst_path, 'w') as dst:
            dst.create_dataset(
                'rle-pad-lzf_data', data=src_group[:, :, :max_len],
                compression='lzf')
