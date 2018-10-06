from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import zipfile


_core_dir = os.path.realpath(os.path.dirname(__file__))
_ids_dir = os.path.join(_core_dir, '_ids')


def get_core_dir():
    key = 'SHAPENET_CORE_PATH'
    if key in os.environ:
        dataset_dir = os.environ[key]
        if not os.path.isdir(dataset_dir):
            raise Exception('%s directory does not exist' % key)
        return dataset_dir
    else:
        raise Exception('%s environment variable not set.' % key)


def get_extracted_core_dir(cat_id=None):
    base = os.environ.get('SHAPENET_EXTRACTION_PATH', '/tmp/shapenet')
    if cat_id is not None:
        base = os.path.join(base, cat_id)
    return base


def get_cat_ids():
    from . import get_cat_ids
    print('Warning: using deprecated `get_cat_ids` in path. Use shapenet.core'
          ' version instead.')
    return get_cat_ids()
    # ids = list(set(
    #     [k[:-4] for k in os.listdir(get_core_dir()) if len(k) > 4 and
    #      k[-4:] == '.zip']))
    # ids.sort()
    # return tuple(ids)


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


def get_example_ids(cat_id):
    with open(get_ids_path(cat_id), 'r') as fp:
        ids = fp.readlines()
    return tuple(id.rstrip() for id in ids)
