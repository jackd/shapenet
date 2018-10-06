from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from .path import get_zip_path, get_zip_file, get_extracted_core_dir


def get_obj_file_dataset(cat_id):
    """Get a DIDS dataset mapping example_ids to obj file objects."""
    import dids.file_io.zip_file_dataset as zfd
    dataset = zfd.ZipFileDataset(get_zip_path(cat_id))

    def key_fn(example_id):
        return os.path.join(cat_id, example_id, 'model.obj')

    def inverse_key_fn(path):
        subpaths = path.split('/')
        if len(subpaths) == 3 and subpaths[2][-4:] == '.obj':
            return subpaths[1]
        else:
            return None

    dataset = dataset.map_keys(key_fn, inverse_key_fn)
    return dataset


def extract_models(cat_id):
    extraction_dir = get_extracted_core_dir(cat_id)
    if os.path.isdir(extraction_dir):
        raise IOError('Directory %s already exists' % extraction_dir)
    _extract_models(cat_id)


def _extract_models(cat_id):
    folder = get_extracted_core_dir()
    print('Extracting obj models for cat %s to %s' % (cat_id, folder))
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with get_zip_file(cat_id) as zf:
        zf.extractall(folder)


def try_extract_models(cat_id):
    from .path import get_example_ids
    folder = get_extracted_core_dir(cat_id)
    if os.path.isdir(folder):
        example_ids = os.listdir(folder)
        if len(example_ids) != len(get_example_ids(cat_id)):
            _extract_models(cat_id)
    else:
        _extract_models(cat_id)


def remove_extracted_models(cat_id, confirm=True):
    import shutil
    extraction_dir = get_extracted_core_dir(cat_id)
    if os.path.isdir(extraction_dir):
        if confirm:
            try:
                get_input = raw_input
            except NameError:
                get_input = input
            confirmed = get_input(
                'Really delete directory %s? (y/N) ' % extraction_dir).lower()
            if confirmed == 'y':
                shutil.rmtree(extraction_dir)
                print('Removed %s' % extraction_dir)
            else:
                print('NOT removing %s' % extraction_dir)
    else:
        print('No directory at %s' % extraction_dir)
