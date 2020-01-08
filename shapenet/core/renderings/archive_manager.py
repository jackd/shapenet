from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from .. import to_cat_id, get_example_ids
from . import archive


class DummyBar(object):
    def __init__(self, *args, **kwargs):
        pass

    def next(self):
        pass

    def finish(self):
        pass


def get_bar(show_progress, *args, **kwargs):
    from progress.bar import IncrementalBar
    return (IncrementalBar if show_progress else DummyBar)(*args, **kwargs)


class ArchiveManager(object):
    def __init__(self, renderings_manager, cat, archive, base_only):
        self._renderings_manager = renderings_manager
        self._cat_id = to_cat_id(cat)
        self._archive = archive
        self._base_only = base_only

    @property
    def archive(self):
        return self._archive

    @property
    def cat_id(self):
        return self._cat_id

    @property
    def renderings_manager(self):
        return self._renderings_manager

    def get_src_paths(self):
        cat_id = self.cat_id
        manager = self.renderings_manager

        if self._base_only:
            example_ids = get_example_ids(cat_id)
            n_views = manager.get_view_params()['n_views']

            for example_id in example_ids:
                for i in range(n_views):
                    yield manager.get_rendering_path(cat_id, example_id, i)
        else:
            cat_dir = manager.get_cat_dir(cat_id)
            for r, _, fns in os.walk(cat_dir):
                for fn in fns:
                    yield os.path.join(r, fn)

    def n_src_paths(self):
        manager = self.renderings_manager
        cat_id = self.cat_id
        if self._base_only:
            return len(get_example_ids(self.cat_id)) \
                * manager.get_view_params()['n_views']
        else:
            cat_dir = manager.get_cat_dir(cat_id)
            c = 0
            for _, __, fns in os.walk(cat_dir):
                c += len(fns)
            return c

    def _do_all(self, fn, show_progress):
        manager = self._renderings_manager
        cat_id = self._cat_id
        archive = self.archive
        print('Getting names...')
        names = set(self.archive.get_names())
        print('%d files found' % len(names))
        cat_dir = manager.get_cat_dir(cat_id)
        base_folder, rest = os.path.split(cat_dir)
        assert(rest == cat_id)
        nrd = len(base_folder) + 1

        n = self.n_src_paths()
        bar = get_bar(show_progress, max=n)
        for path in self.get_src_paths():
            bar.next()
            name = path[nrd:]
            if name not in names:
                fn(archive, path, name)
        bar.finish()

    def unpack(self):
        manager = self._renderings_manager
        cat_id = self._cat_id
        archive = self.archive

        cat_dir = manager.get_cat_dir(cat_id)
        base_folder, rest = os.path.split(cat_dir)
        assert(rest == cat_id)
        print('Extracting files at %s' % archive.path)
        archive.extractall(base_folder)

    def check(self):
        def fn(archive, src_path, name):
            raise RuntimeError('%s not present' % name)
        self._do_all(fn, False)
        print('Check complete: %s' % str(self.archive))

    def add(self):
        def fn(archive, src_path, name):
            archive.add(src_path, name)
        self._do_all(fn, True)
        print('Add complete: %s' % str(self.archive))


def get_archive_path(renderings_manager, cat, base_only=True, format='zip'):
    cat_id = to_cat_id(cat)
    fn = ('%s-base.%s' if base_only else '%s.%s') % (cat_id, format)
    return os.path.join(renderings_manager.root_dir, 'renderings', fn)


def get_archive(
        renderings_manager, cat, base_only=True, format='zip', mode='r'):
    return archive.get_archive(
        get_archive_path(renderings_manager, cat, base_only, format), mode)


def get_archive_manager(
        renderings_manager, cat, base_only=True, format='zip', mode='r'):
    archive = get_archive(renderings_manager, cat, base_only, format, mode)
    return ArchiveManager(
        renderings_manager, cat, archive, base_only)
