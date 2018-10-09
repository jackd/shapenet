from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import tarfile


def add_renderings(manager, cat, base_only=True, path=None):
    from progress.bar import IncrementalBar
    from shapenet.core import get_example_ids, to_cat_id
    cat_id = to_cat_id(cat)
    n_renderings = manager.get_render_params()['n_renderings']
    root_dir = manager.root_dir
    nrd = len(root_dir) + 1
    if path is None:
        path = get_renderings_tar_path(manager, cat_id)

    print('Compressing data %s -> %s' % (cat_id, path))
    if base_only:
        with tarfile.open(path, 'a') as tar:
            example_ids = get_example_ids(cat_id)
            n = len(example_ids)
            bar = IncrementalBar(max=n)
            for i, example_id in enumerate(example_ids):
                for i in range(n_renderings):
                    path = manager.get_rendering_path((cat_id, example_id), i)
                    assert(path.startswith(root_dir))
                    tar.add(path, path[nrd:])
                bar.next()
            bar.finish()
    else:
        import shutil
        folder = manager.get_cat_dir(cat_id)
        folder, fn = os.path.split(folder)
        assert(fn == cat_id)
        if path.endswith('.tar'):
            path = path[:-4]
        shutil.make_archive(path, 'tar', folder, fn, verbose=1)


def get_renderings_tar_path(manager, cat_id):
    return os.path.join(manager.root_dir, 'renderings', '%s.tar' % cat_id)


def get_renderings_tar(manager, cat_id, mode='r'):
    return tarfile.open(get_renderings_tar_path(manager, cat_id), mode=mode)
