def create_point_clouds(
        n_samples, cat_desc, example_ids=None, overwrite=False):
    from shapenet.core.point_clouds.core import PointCloudAutoSavingManager
    from shapeent.core import cat_desc_to_id
    cat_id = cat_desc_to_id(cat_desc)
    PointCloudAutoSavingManager(cat_id, n_samples, example_ids).save_all(
        overwrite=overwrite)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str,)
    parser.add_argument('-n', '--n_samples', default=16384, type=int,
                        help='number of points in clouds')
    parser.add_argument('-i', '--example_ids', nargs='*')
    parser.add_argument('-o', '--overwrite', action='store_true')
    args = parser.parse_args()
    create_point_clouds(
        args.n_samples, args.cat, args.example_ids, args.overwrite)
