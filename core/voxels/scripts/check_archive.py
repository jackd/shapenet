def check_archive(cat_desc, voxel_dim, example_ids=None):
    from shapenet.core import cat_desc_to_id, get_example_ids
    from shapenet.core.voxels.config import VoxelConfig
    cat_id = cat_desc_to_id(cat_desc)
    if example_ids is None or len(example_ids) == 0:
        example_ids = get_example_ids(cat_id)
    config = VoxelConfig(voxel_dim=voxel_dim)
    n_absent = 0
    with config.get_zip_file(cat_id) as zf:
        namelist = set(zf.namelist())
    for example_id in example_ids:
        if config.get_binvox_subpath(cat_id, example_id) not in namelist:
            n_absent += 1

    if n_absent == 0:
        print('All %d %s voxels present' % (len(example_ids), cat_desc))
    else:
        print('%d / %d voxel files missing from %s' %
              (n_absent, len(example_ids), cat_desc))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str)
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-i', '--example_ids', nargs='*')
    parser.add_argument('-n', '--voxel_dim', default=32, type=int)

    args = parser.parse_args()
    check_archive(
        args.cat, args.voxel_dim, args.example_ids)
