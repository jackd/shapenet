from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import zipfile


def get_annot_dir():
    from ...config import config
    return config['core_annotations_dir']


annot_dir = get_annot_dir()


def get_zip_path():
    return os.path.join(annot_dir, 'shapenetcore_partanno_v0.zip')


def get_zip_file():
    return zipfile.ZipFile(get_zip_path(), 'r')


def _get_subpath(cat_id, example_id, topic, ext):
    fn = '%s.%s' % (example_id, ext)
    return os.path.join('PartAnnotation', cat_id, topic, fn)
