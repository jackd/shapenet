#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# import os
# from progress.bar import IncrementalBar
# from shapenet.core.voxels.datasets import get_manager
# from shapenet.core.voxels.config import get_config
# from shapenet.core import get_old_example_ids, get_example_ids
# from shapenet.r2n2 import get_cat_ids
#
#
# def convert_orthographic(old_indices, new_ids, config, cat_id, dims):
#     src = get_manager(
#         config, cat_id, key='rle', compression='lzf', shape_key='pad')
#     dst = get_manager(config, cat_id, key='zip')
#     dst.create_from(src)
#
#
# def convert_all_orthographic():
#     for cat_id in get_cat_ids():
#         for voxel_dim in (32, 64, 128, 256):
#             old_ids = get_old_example_ids(cat_id)
#             old_indices = {k: i for i, k in enumerate(old_ids)}
#             new_ids = get_example_ids(cat_id)
#             config = get_config(voxel_dim)
#             config = config.filled('orthographic')
#             convert_orthographic(
#                 old_indices, new_ids, config, cat_id, (voxel_dim,)*3)


# def convert(old_indices, new_ids, config, cat_id, dims):
#     import zipfile
#     src_path = get_manager(config, cat_id, key='zip').path
#     temp = get_manager(
#         config, cat_id, key='rle', compression='lzf', shape_key='ind')
#     temp_path = temp.path
#     if os.path.isfile(temp_path):
#         # raise Exception(temp_path)
#         os.remove(temp_path)
#     with zipfile.ZipFile(src_path) as src_zf:
#         with temp._get_dataset(id_keys=True, mode='a') as temp_ds:
#             print('Converting %s ...' % src_path)
#             bar = IncrementalBar(max=len(new_ids))
#             for example_id in new_ids:
#                 bar.next()
#                 temp_ds[example_id] = RleVoxels.from_file(
#                     src_zf.open('%s/%s.binvox' % (cat_id, example_id)))
#             bar.finish()
#     dst_manager = get_manager(
#         config, cat_id, key='rle', compression='lzf', shape_key='pad')
#     dst_manager.create_from(temp)
#     temp.delete()
#
#
# def convert_all_zip():
#     for cat_id in get_cat_ids():
#         for voxel_dim in (32, 64, 128):
#             old_ids = get_old_example_ids(cat_id)
#             old_indices = {k: i for i, k in enumerate(old_ids)}
#             new_ids = get_example_ids(cat_id)
#             config = get_config(voxel_dim)
#             convert(
#                 old_indices, new_ids, config, cat_id, (voxel_dim,)*3)


# convert_all_orthographic()
# convert_all_zip()
