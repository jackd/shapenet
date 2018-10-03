#!/usr/bin/python


def convert_multi(
        cat_id, example_ids, overwrite=False, filled=False, fill_alg=None,
        archive=False, delete_src=False, **kwargs):
    from shapenet.core.voxels.config import VoxelConfig
    config = VoxelConfig(**kwargs)
    if filled:
        config = config.filled(fill_alg)
    config.create_voxel_data(cat_id, example_ids, overwrite=overwrite)
    if archive:
        config.create_zip_file(
            cat_id, overwrite=overwrite, delete_src=delete_src)


def main(
        cat_descs, voxel_dim, overwrite, filled, fill_alg, archive,
        delete_src):
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
            filled=filled, fill_alg=fill_alg, archive=archive,
            delete_src=delete_src)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cats', nargs='*')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-d', '--voxel_dim', type=int, default=32)
    parser.add_argument('-f', '--filled', action='store_true')
    parser.add_argument(
        '-a', '--alg', type=str, default='filled', help='fill algorithm',
        choices=['filled', 'orthographic'])
    parser.add_argument('--archive', action='store_true')
    parser.add_argument('--delete_src', action='store_true')

    args = parser.parse_args()
    main(args.cats, voxel_dim=args.voxel_dim, overwrite=args.overwrite,
         filled=args.filled, fill_alg=args.alg, archive=args.archive,
         delete_src=args.delete_src)
