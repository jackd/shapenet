#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from progress.bar import IncrementalBar
from shapenet.core.path import get_ids_path
from shapenet.core.path import get_cat_ids
from shapenet.core.path import get_example_ids_from_zip
from shapenet.core.path import get_example_ids


def create(cat_ids):
    print('Creating example_ids')
    bar = IncrementalBar(max=len(cat_ids))
    for cat_id in cat_ids:
        path = get_ids_path(cat_id)
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            os.makedirs(d)
        example_ids = get_example_ids_from_zip(cat_id)
        with open(path, 'w') as fp:
            fp.writelines(
                ('%s\n' % example_id for example_id in example_ids))
        bar.next()
    bar.finish()


def check(cat_ids):
    print('Checking...')
    bar = IncrementalBar(max=len(cat_ids))
    for cat_id in cat_ids:
        actual = get_example_ids(cat_id)
        original = get_example_ids_from_zip(cat_id)
        if tuple(actual) != tuple(original):
            raise IOError('ids for cat_id "%s" not consistent' % cat_id)
        bar.next()
    bar.finish()
    print('All ids consistent!')


cat_ids = get_cat_ids()
# create(cat_ids)
check(cat_ids)
