def create_point_clouds(
        n_samples, cat_desc, example_ids=None, normals=False, overwrite=False):
    from shapenet.core.point_clouds import PointCloudAutoSavingManager
    from shapenet.core.point_clouds import CloudNormalAutoSavingManager
    from shapenet.core import cat_desc_to_id
    cat_id = cat_desc_to_id(cat_desc)
    if normals:
        manager = CloudNormalAutoSavingManager(cat_id, n_samples, example_ids)
    else:
        manager = PointCloudAutoSavingManager(cat_id, n_samples, example_ids)
    manager.save_all(overwrite=overwrite)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str,)
    parser.add_argument('-n', '--n_samples', default=16384, type=int,
                        help='number of points in clouds')
    parser.add_argument('-i', '--example_ids', nargs='*')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('--normals', action='store_true')
    args = parser.parse_args()
    kwargs = dict(
        example_ids=args.example_ids, normals=args.normals,
        overwrite=args.overwrite, n_samples=args.n_samples)

    if args.cat == 'ALL':
        from shapenet.core import get_cat_ids
        from shapenet.core import cat_id_to_desc
        cat_descs = tuple(cat_id_to_desc(c) for c in get_cat_ids())
        for i, cat in enumerate(cat_descs):
            print('Generating data for cat %s, %d / %d' %
                  (cat, i, len(cat_descs)))
            create_point_clouds(cat_desc=cat, **kwargs)
    else:
        create_point_clouds(cat_desc=cat, **kwargs)
