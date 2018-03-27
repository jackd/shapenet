

def create_archive(cat_desc, voxel_dim, example_ids=None, overwrite=False):
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
            zf.write(src, dst)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str)
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-d', '--voxel_dim', type=int, default=32)
    parser.add_argument('-i', '--example_ids', nargs='*')

    args = parser.parse_args()
    create_archive(
        args.cat, args.voxel_dim, args.example_ids, args.overwrite)
