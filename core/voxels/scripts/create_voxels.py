#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def convert_multi(
        cat_id, example_ids, voxel_dim, overwrite=False, fill_alg=None,
        alt=False, hdf5=False, zip=False, delete_src=False):
    from shapenet.core.voxels.config import get_config
    config = get_config(voxel_dim, alt)
    if fill_alg is not None:
        config = config.filled(fill_alg)
    config.create_voxel_data(cat_id, example_ids, overwrite=overwrite)
    if zip:
        config.create_zip_file(
            cat_id, overwrite=overwrite, delete_src=delete_src)
    elif hdf5:
        config.create_hdf5_data(cat_id, delete_src=delete_src)


def main(
        cat_descs, voxel_dim, overwrite, alt, fill_alg, zip,
        hdf5, delete_src):
    from shapenet.core import cat_desc_to_id, get_cat_ids
    from shapenet.core import get_example_ids
    if len(cat_descs) == 0:
        cat_ids = get_cat_ids()
    else:
        cat_ids = [cat_desc_to_id(cat_desc) for cat_desc in cat_descs]
    for i, cat_id in enumerate(cat_ids):
        print('Processing cat_id %s, %d / %d' % (cat_id, i+1, len(cat_ids)))
        example_ids = get_example_ids(cat_id)
        convert_multi(
            cat_id, example_ids, overwrite=overwrite, voxel_dim=voxel_dim,
            alt=alt, fill_alg=fill_alg, zip=zip,
            hdf5=hdf5, delete_src=delete_src)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cats', nargs='*')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-d', '--voxel_dim', type=int, default=32)
    parser.add_argument('--alt', action='store_true')
    parser.add_argument(
        '-a', '--alg', type=str, default=None, help='fill algorithm',
        choices=[None, 'filled', 'orthographic'])
    parser.add_argument('--zip', action='store_true')
    parser.add_argument('--hdf5', action='store_true')
    parser.add_argument('--delete_src', action='store_true')

    args = parser.parse_args()
    if args.zip and args.hdf5:
        raise IOError('Only one of `zip` and `hdf5` can be True')

    main(args.cats, voxel_dim=args.voxel_dim, overwrite=args.overwrite,
         alt=args.alt, fill_alg=args.alg, zip=args.zip,
         hdf5=args.hdf5, delete_src=args.delete_src)
