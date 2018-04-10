

def create_archive(cat_desc, voxel_dim, example_ids=None, overwrite=False):
    import os
    import zipfile
    from shapenet.core.voxels.config import VoxelConfig
    from shapenet.core import get_example_ids, cat_desc_to_id
    cat_id = cat_desc_to_id(cat_desc)

    if example_ids is None or len(example_ids) == 0:
        example_ids = get_example_ids(cat_id)
    config = VoxelConfig(voxel_dim)
    with zipfile.ZipFile(config.get_zip_path(cat_id), 'a') as zf:
        if not overwrite:
            namelist = set(zf.namelist())
        for example_id in example_ids:
            dst = config.get_binvox_subpath(cat_id, example_id)
            if not overwrite and dst in namelist:
                continue
            src = config.get_binvox_path(cat_id, example_id)
            if os.path.isfile(src):
                zf.write(src, dst)
            else:
                print('No file at %s for %s/%s: skipping' %
                      (src, cat_id, example_id))


def create_all_archives(voxel_dim, overwrite=False):
    from shapenet.core import get_cat_ids, cat_id_to_desc
    cat_ids = get_cat_ids()
    for cat_id in cat_ids:
        cat_desc = cat_id_to_desc(cat_id)
        print('Creating archive: %s' % cat_desc)
        create_archive(cat_desc, voxel_dim, overwrite=overwrite)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str, nargs='?')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-d', '--voxel_dim', type=int, default=32)
    parser.add_argument('-i', '--example_ids', nargs='*')

    args = parser.parse_args()
    if args.cat is None:
        create_all_archives(args.voxel_dim, overwrite=args.overwrite)
    else:
        create_archive(
            args.cat, args.voxel_dim, args.example_ids, args.overwrite)
