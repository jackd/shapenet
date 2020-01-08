def generate_mesh_data(cat_desc, overwrite=False):
    from shapenet.core import cat_desc_to_id
    from shapenet.core.meshes import generate_mesh_data

    cat_id = cat_desc_to_id(cat_desc)
    generate_mesh_data(cat_id, overwrite=overwrite)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str, nargs='+')
    parser.add_argument('-o', '--overwrite', action='store_true')

    args = parser.parse_args()
    for cat in args.cat:
        generate_mesh_data(cat, args.overwrite)
