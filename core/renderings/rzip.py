from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import zipfile


def add_all(dst_path, src_dir, base_path):
    with zipfile.ZipFile(
            dst_path, 'a', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        dir = os.path.join(src_dir, base_path)
        nrl = len(src_dir) + 1
        for root, _, filenames in os.walk(dir):
            for name in filenames:
                name = os.path.join(root, name)
                zf.write(name, name[nrl:])


def add_renderings(manager, cat, base_only=True, path=None):
    from progress.bar import IncrementalBar
    from shapenet.core import get_example_ids, to_cat_id
    cat_id = to_cat_id(cat)
    n_renderings = manager.get_render_params()['n_renderings']
    root_dir = manager.root_dir
    nrd = len(root_dir) + 1
    if path is None:
        path = get_renderings_zip_path(manager, cat_id)

    print('Compressing data %s -> %s' % (cat_id, path))
    if base_only:
        with zipfile.ZipFile(
                path, 'a', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            example_ids = get_example_ids(cat_id)
            n = len(example_ids)
            bar = IncrementalBar(max=n)
            for i, example_id in enumerate(example_ids):
                for i in range(n_renderings):
                    path = manager.get_rendering_path((cat_id, example_id), i)
                    assert(path.startswith(root_dir))
                    zf.write(path, path[nrd:])
                bar.next()
            bar.finish()
    else:
        import shutil
        folder = manager.get_cat_dir(cat_id)
        folder, fn = os.path.split(folder)
        assert(fn == cat_id)
        if path.endswith('.zip'):
            path = path[:-4]
        shutil.make_archive(path, 'zip', folder, fn, verbose=1)


def get_renderings_zip_path(manager, cat_id):
    return os.path.join(manager.root_dir, 'renderings', '%s.zip' % cat_id)


def get_renderings_zip(manager, cat_id, mode='r'):
    return zipfile.ZipFile(get_renderings_zip_path(manager, cat_id), mode=mode)
