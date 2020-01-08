#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from progress.bar import IncrementalBar
from shapenet.core.path import get_cat_ids
from shapenet.core.path import get_example_ids_from_zip
from shapenet.core.path import get_example_ids
from shapenet.core import create_ids


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


def main(cat_ids):
    print('Creating example_ids')
    create_ids(cat_ids)
    check(cat_ids)


main(get_cat_ids())
