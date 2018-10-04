#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os

cats = (
    'plane',
    'bench',
    'cabinet',
    'car',
    'chair',
    'monitor',
    'lamp',
    'speaker',
    'rifle',
    'sofa',
    'table',
    'cellphone',
    'watercraft'
)
assert(len(cats) == 13)


def main(voxel_dim, fill_alg, zip, hdf5):
    from shapenet.core.voxels import VoxelConfig
    from shapenet.core import cat_desc_to_id
    config = VoxelConfig(voxel_dim)
    if fill_alg is not None:
        config = config.filled(fill_alg)
    for cat in cats:
        cat_id = cat_desc_to_id(cat)
        if zip:
            path = config.get_zip_path(cat_id)
        elif hdf5:
            path = config.get_hdf5_path(cat_id)

        present = os.path.isfile(path)
        print('%s: %s' % ('present' if present else 'absent', cat))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--voxel_dim', type=int, default=32)
    parser.add_argument(
        '-a', '--alg', type=str, default=None, help='fill algorithm',
        choices=[None, 'filled', 'orthographic'])
    parser.add_argument('--zip', action='store_true')
    parser.add_argument('--hdf5', action='store_true')

    args = parser.parse_args()
    if args.zip == args.hdf5:
        raise IOError('Exactly one of `zip` and `hdf5` must be True')

    main(voxel_dim=args.voxel_dim, fill_alg=args.alg, zip=args.zip,
         hdf5=args.hdf5)
