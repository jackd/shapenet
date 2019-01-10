from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from .. import path

data_dir = path.get_data_dir('r2n2')


def get_binvox_subpath(cat_id=None, example_id=None):
    args = ['ShapeNetVox32']
    if cat_id is not None:
        args.append(cat_id)
        if example_id is not None:
            args.extend((example_id, 'model.binvox'))
    return os.path.join(*args)


def get_renderings_subpath(cat_id=None, example_id=None, data_id=None):
    args = ['ShapeNetRendering']
    if cat_id is not None:
        args.append(cat_id)
        if example_id is not None:
            args.append(example_id)
            if data_id is not None:
                args.append('rendering')
                if isinstance(data_id, int):
                    args.append('%02d.png' % data_id)
                elif isinstance(data_id, (str, unicode)):
                    args.append(data_id)
                else:
                    raise ValueError('Unrecognized data_id `%s`' % data_id)

    return os.path.join(*args)


def get_binvox_path(cat_id=None, example_id=None):
    return os.path.join(data_dir, get_binvox_subpath(cat_id, example_id))


def get_renderings_path(cat_id=None, example_id=None, data_id=None):
    return os.path.join(
        data_dir, get_renderings_subpath(cat_id, example_id, data_id))
