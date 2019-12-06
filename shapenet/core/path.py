from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import zipfile
from .. import config


def get_core_dir():
    return config.config['core_dir']


def get_data_dir(*args):
    from .. import path
    return path.get_data_dir('core', *args)


_ids_dir = get_data_dir('ids')


def get_extracted_core_dir(cat_id=None):
    args = 'extracted',
    if cat_id is not None:
        args = args + (cat_id,)
    return get_data_dir(*args)


def get_csv_path(cat_id):
    return os.path.join(get_core_dir(), '%s.csv' % cat_id)


def get_zip_path(cat_id):
    return os.path.join(get_core_dir(), '%s.zip' % cat_id)


def get_test_train_split_path():
    return os.path.join(
        os.path.realpath(os.path.dirname(__file__)), 'split.csv')


def get_zip_file(cat_id):
    return zipfile.ZipFile(get_zip_path(cat_id))


def get_example_subdir(cat_id, example_id):
    return os.path.join(cat_id, example_id)


def get_obj_subpath(cat_id, example_id):
    return os.path.join(cat_id, example_id, 'model.obj')


def get_mtl_subpath(cat_id, example_id):
    return os.path.join(cat_id, example_id, 'model.mtl')


def _get_example_ids_from_zip(cat_id, category_zipfile):
    start = len(cat_id) + 1
    end = -len('model.obj')-1
    names = [
        n[start:end] for n in category_zipfile.namelist() if n[-4:] == '.obj']
    return names


def get_example_ids_from_zip(cat_id, category_zipfile=None):
    if category_zipfile is None:
        with get_zip_file(cat_id) as f:
            return _get_example_ids_from_zip(cat_id, f)
    else:
        return _get_example_ids_from_zip(cat_id, category_zipfile)


def get_ids_path(cat_id):
    return os.path.join(_ids_dir, '%s.txt' % cat_id)
