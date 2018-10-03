#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def create_archive(
        cat_desc, voxel_dim, example_ids=None, overwrite=False, filled=False,
        delete_src=False, fill_alg='filled'):
    from shapenet.core.voxels.config import VoxelConfig
    from shapenet.core import get_example_ids, cat_desc_to_id
    cat_id = cat_desc_to_id(cat_desc)

    if example_ids is None or len(example_ids) == 0:
        example_ids = get_example_ids(cat_id)
    config = VoxelConfig(voxel_dim)
    if filled:
        config = config.filled(fill_alg)
    config.create_zip_file(
        cat_id, example_ids=example_ids, overwrite=overwrite,
        delete_src=delete_src)


def create_all_archives(
        voxel_dim, overwrite=False, filled=False, delete_src=False,
        fill_alg='filled'):
    from shapenet.core import get_cat_ids, cat_id_to_desc
    cat_ids = get_cat_ids()
    for cat_id in cat_ids:
        cat_desc = cat_id_to_desc(cat_id)
        print('Creating archive: %s' % cat_desc)
        create_archive(
            cat_desc, voxel_dim, overwrite=overwrite, filled=filled,
            delete_src=delete_src, fill_alg=fill_alg)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str, nargs='?')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-d', '--voxel_dim', type=int, default=32)
    parser.add_argument('-i', '--example_ids', nargs='*')
    parser.add_argument('-f', '--filled', action='store_true')
    parser.add_argument(
        '-a', '--alg', type=str, choices=['filled', 'orthographic'],
        default='filled')
    parser.add_argument('--delete_src', action='store_true')

    args = parser.parse_args()
    kwargs = dict(
        overwrite=args.overwrite,
        filled=args.filled,
        delete_src=args.delete_src,
        fill_alg=args.alg,
    )
    if args.cat is None:
        create_all_archives(args.voxel_dim, **kwargs)
    else:
        create_archive(
            args.cat, args.voxel_dim, args.example_ids, **kwargs)
