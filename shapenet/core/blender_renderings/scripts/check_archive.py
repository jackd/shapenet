"""Checks rendered archive for renderings of all example ids."""


def check_zip(cat_desc, shape, n_images):
    import zipfile
    from shapenet.core.blender_renderings.config import RenderConfig
    from shapenet.core import cat_desc_to_id, get_example_ids
    cat_id = cat_desc_to_id(cat_desc)

    config = RenderConfig(shape=shape, n_images=n_images)
    rendered_ids = set()
    with zipfile.ZipFile(config.get_zip_path(cat_id)) as zf:
        for name in zf.namelist():
            rendered_ids.add(name.split('/')[1])

    not_rendered_count = 0
    example_ids = get_example_ids(cat_id)
    for example_id in example_ids:
        if example_id not in rendered_ids:
            print(example_id)
            not_rendered_count += 1

    if not_rendered_count > 0:
        print('%d / %d not rendered' % (not_rendered_count, len(example_ids)))
    else:
        print('All %d %ss rendered!' % (len(example_ids), cat_desc))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str)
    parser.add_argument('--shape', type=int, nargs=2, default=[192, 256])
    parser.add_argument('-n', '--n_images', type=int, default=8)
    args = parser.parse_args()
    check_zip(args.cat, args.shape, args.n_images)
