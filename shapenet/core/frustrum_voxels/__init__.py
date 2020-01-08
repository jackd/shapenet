from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np
import h5py
from ..voxels.datasets import get_manager as get_voxel_manager, GROUP_KEY

from util3d.transform.frustrum import voxel_values_to_frustrum
from util3d.transform.nonhom import get_eye_to_world_transform
from util3d.voxel.binvox import DenseVoxels, RleVoxels


def _make_dir(filename):
    folder = os.path.dirname(filename)
    if not os.path.isdir(folder):
        os.makedirs(folder)


def convert(vox, eye, ray_shape, f):
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
        voxel_config, view_id, out_dim, cat_id, code=None):
    from ..path import get_data_dir
    fn = ('%s.hdf5' % cat_id) if code is None else (
        '%s_%s.hdf5' % (code, cat_id))
    return os.path.join(
        get_data_dir('frustrum_voxels'), voxel_config.voxel_id, view_id,
        'v%03d' % out_dim, fn)


def get_frustrum_voxels_path(
        voxel_config, view_id, out_dim, cat_id):
    return _get_frustrum_voxels_path(
        voxel_config, view_id, out_dim, cat_id)


def get_frustrum_voxels_data(voxel_config, view_id, out_dim, cat_id):
    return h5py.File(get_frustrum_voxels_path(
        voxel_config, view_id, out_dim, cat_id), 'r')


def create_temp_frustrum_voxels(
        view_manager, voxel_config, out_dim, cat_id, compression='lzf'):
    from progress.bar import IncrementalBar
    view_params = view_manager.get_view_params()
    n_views = view_params['n_views']
    f = view_params['f']
    in_dims = (voxel_config.voxel_dim,) * 3
    ray_shape = (out_dim,) * 3
    example_ids = tuple(view_manager.get_example_ids(cat_id))
    n0 = len(example_ids)

    temp_path = _get_frustrum_voxels_path(
            voxel_config, view_manager.view_id, out_dim,
            cat_id, code='temp')
    _make_dir(temp_path)
    with h5py.File(temp_path, 'a') as vox_dst:
        attrs = vox_dst.attrs
        prog = attrs.get('prog', 0)
        if prog == n0:
            return temp_path

        attrs.setdefault('n_views', n_views)
        max_len = attrs.setdefault('max_len', 0)

        vox_manager = get_voxel_manager(
            voxel_config, cat_id, key='rle',
            compression=compression, shape_key='pad')
        vox_manager.get_dataset()  # ensure data exists
        assert(vox_manager.has_dataset())
        with h5py.File(vox_manager.path, 'r') as vox_src:
            rle_src = vox_src[GROUP_KEY]

            n, m = rle_src.shape
            max_max_len = m * 3
            assert(n == n0)

            print(
                'Creating temp rle frustrum voxel data at %s' % temp_path)
            rle_dst = vox_dst.require_dataset(
                GROUP_KEY, shape=(n, n_views, max_max_len),
                dtype=np.uint8, compression=compression)
            bar = IncrementalBar(max=n-prog)
            for i in range(prog, n):
                bar.next()
                voxels = RleVoxels(np.array(rle_src[i]), in_dims)
                eye = view_manager.get_camera_positions(cat_id, example_ids[i])
                for j in range(n_views):
                    out = convert(voxels, eye[j], ray_shape, f)
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
                attrs['prog'] = i+1
            bar.finish()
    return temp_path


def _shrink_data(temp_path, dst_path, chunk_size=100, compression='lzf'):
    from progress.bar import IncrementalBar
    print('Shrinking data to fit.')
    with h5py.File(temp_path, 'r') as src:
        max_len = int(src.attrs['max_len'])
        src_group = src[GROUP_KEY]
        _make_dir(dst_path)
        with h5py.File(dst_path, 'w') as dst:
            n_examples, n_renderings = src_group.shape[:2]
            dst_dataset = dst.create_dataset(
                GROUP_KEY, shape=(n_examples, n_renderings, max_len),
                dtype=np.uint8, compression=compression)
            bar = IncrementalBar(max=n_examples // chunk_size)
            for i in range(0, n_examples, chunk_size):
                stop = min(i + chunk_size, n_examples)
                dst_dataset[i:stop] = src_group[i:stop, :, :max_len]
                bar.next()
            bar.finish()


# def _concat_data(temp_path, dst_path):
#     from progress.bar import IncrementalBar
#     from util3d.voxel import rle
#     print('Concatenating data')
#     with h5py.File(temp_path, 'r') as src:
#         src_group = src[GROUP_KEY]
#         _make_dir(dst_path)
#         with h5py.File(dst_path, 'w') as dst:
#             n_examples, n_renderings = src_group.shape[:2]
#             n_total = n_examples * n_renderings
#             starts = np.empty(dtype=np.int64, shape=(n_total+1,))
#             print('Computing starts...')
#             k = 1
#             start = 0
#             starts[0] = start
#             bar = IncrementalBar(max=n_examples)
#             for i in range(n_examples):
#                 bar.next()
#                 example_data = np.array(src_group[i])
#                 for j in range(n_renderings):
#                     data = rle.remove_length_padding(example_data[j])
#                     start += len(data)
#                     starts[k] = start
#                     k += 1
#             bar.finish()
#             assert(k == n_total+1)
#             dst.create_dataset('starts', data=starts)
#             values = dst.create_dataset(
#                 'values', dtype=np.uint8, shape=(starts[-1],))

#             k = 0
#             print('Transfering data...')
#             bar = IncrementalBar(max=n_examples)
#             for i in range(n_examples):
#                 example_data = np.array(src_group[i])
#                 bar.next()
#                 for j in range(n_renderings):
#                     values[starts[k]: starts[k+1]] = \
#                         rle.remove_length_padding(example_data[j])
#                     k += 1
#             bar.finish()
#             assert(k == n_total)


def create_frustrum_voxels(
        view_manager, voxel_config, out_dim, cat_id, compression='lzf'):
    kwargs = dict(
        voxel_config=voxel_config,
        out_dim=out_dim, cat_id=cat_id)
    dst_path = _get_frustrum_voxels_path(
        view_id=view_manager.view_id, code=None, **kwargs)
    if os.path.isfile(dst_path):
        print('Already present.')
        return
    temp_path = create_temp_frustrum_voxels(
        view_manager=view_manager, compression=compression, **kwargs)
    _shrink_data(temp_path, dst_path, compression=compression)
    # _concat_data(temp_path, dst_path)


# def fix(view_manager, voxel_config, out_dim, cat_id, example_index,
#         view_index, example_ids, compression='lzf'):
#     # from util3d.voxel.rle import length
#     dst_path = _get_frustrum_voxels_path(
#         manager_dir=view_manager.root_dir, code=None,
#         voxel_config=voxel_config, out_dim=out_dim, cat_id=cat_id)
#     # load src data
#     vox_manager = get_voxel_manager(
#         voxel_config, cat_id, key='rle',
#         compression=compression, shape_key='pad')
#     if not vox_manager.has_dataset():
#         raise RuntimeError('No dataset')
#     with h5py.File(vox_manager.path, 'r') as vox_src:
#         rle_src = vox_src[GROUP_KEY]
#         voxels = RleVoxels(
#             np.array(rle_src[example_index]),
#             (voxel_config.voxel_dim,) * 3)
#     eye = view_manager.get_camera_positions(
#         cat_id, example_ids[example_index])
#     f = view_manager.get_view_params()['f']
#     # convert
#     rle_data = convert(voxels, eye, (out_dim,)*3, f).rle_data()
#     # save
#     with h5py.File(dst_path, 'a') as dst:
#         dst_group = dst[GROUP_KEY]
#         padded_rle_data = np.zeros((dst_group.shape[2],), dtype=np.uint8)
#         padded_rle_data[:len(rle_data)] = rle_data
#         dst_group[example_index, view_index] = padded_rle_data

#     # with h5py.File(dst_path, 'r') as dst:
#     #     dst_group = dst[GROUP_KEY]
#     #     old_data = np.array(dst_group[example_index, view_index])
#     #     print(length(old_data))
#     #     print(length(rle_data))

#     # start = 500
#     # end = 520
#     # print(rle_data[start:end])
#     # print(old_data[start:end])
#     # print(out_dim)
#     # print(out_dim**3)
#     # print(length(rle_data))
#     # print(length(old_data))
