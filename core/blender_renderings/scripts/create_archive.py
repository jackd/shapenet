"""Creates or adds to an archive of renderings."""


def create_archive(cat_desc, shape=(192, 256), n_images=8, example_ids=None):
    import os
    from shapenet.core import cat_desc_to_id
    from shapenet.core import get_example_ids
    from shapenet.core.blender_renderings.config import RenderConfig
    from progress.bar import IncrementalBar
    import zipfile
    cat_id = cat_desc_to_id(cat_desc)
    if example_ids is None or len(example_ids) == 0:
        example_ids = get_example_ids(cat_id)
    config = RenderConfig(shape=shape, n_images=n_images)
    zip_path = config.get_zip_path(cat_id)
    with zipfile.ZipFile(zip_path, mode='a', allowZip64=True) as zf:
        bar = IncrementalBar(max=len(example_ids))
        for example_id in example_ids:
            example_dir = config.get_example_dir(cat_id, example_id)
            if not os.path.isdir(example_dir):
                print('No directory at %s' % example_dir)
            else:
                for fn in os.listdir(example_dir):
                    src = os.path.join(example_dir, fn)
                    dst = os.path.join(cat_id, example_id, fn)
                    zf.write(src, dst)
            bar.next()
        bar.finish()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str)
    parser.add_argument('--shape', type=int, nargs=2, default=[192, 256])
    parser.add_argument('-n', '--n_images', type=int, default=8)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-i', '--example_ids', nargs='*')
    args = parser.parse_args()
    create_archive(args.cat, args.shape, args.n_images, args.example_ids)
