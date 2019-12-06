def check_mesh_data(cat_desc):
    from shapenet.core import cat_desc_to_id, get_example_ids
    from shapenet.core.meshes import get_mesh_dataset
    cat_id = cat_desc_to_id(cat_desc)
    example_ids = get_example_ids(cat_id)
    n_absent = 0
    with get_mesh_dataset(cat_id) as ds:
        for example_id in example_ids:
            if example_id not in ds:
                n_absent += 1

    n = len(example_ids)
    if n_absent == 0:
        print('All %d %s meshes present!' % (n, cat_desc))
    else:
        print('%d / %d %s meshes absent' % (n_absent, n, cat_desc))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str)

    args = parser.parse_args()
    check_mesh_data(args.cat)
