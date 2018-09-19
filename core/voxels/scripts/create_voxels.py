#!/usr/bin/python


def convert_multi(cat_id, example_ids, overwrite=False, **kwargs):
    from shapenet.core.voxels.config import VoxelConfig
    config = VoxelConfig(**kwargs)
    config.create_voxel_data(cat_id, example_ids, overwrite=overwrite)


def main(cat_descs, voxel_dim, overwrite):
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
            cat_id, example_ids, overwrite=overwrite, voxel_dim=voxel_dim)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cats', nargs='*')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-d', '--voxel_dim', type=int, default=32)

    args = parser.parse_args()
    main(args.cats, voxel_dim=args.voxel_dim, overwrite=args.overwrite)
