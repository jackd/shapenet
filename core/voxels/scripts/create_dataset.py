#!/usr/bin/python

"""
Script for creating/converting voxel data formats.

Example usage:
./create_dataset.py --cat=car,plane --voxel_dim=128 \
    --format=rle --overwrite=True --compression=gzip --shape=pad
    --src_format=file
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags, app
FLAGS = flags.FLAGS

# VoxelConfig args
flags.DEFINE_integer('voxel_dim', default=32, help='voxel dimension')
flags.DEFINE_boolean(
    'alt', default=False, help='use alternative base VoxelConfig')
flags.DEFINE_string('fill', default=None, help='optional fill algorithm')

flags.DEFINE_list(
    'cat', default=None, help='cat desc(s) to create (comma separated)')

flags.DEFINE_boolean(
    'overwrite', default=False, help='overwrite existing data')
flags.DEFINE_string(
    'format', default='file',
    help='input format, one of '
         '["file", "zip", "rle", "brle"]')
flags.DEFINE_string(
    'shape', default=None, help='one of ["pad", "jag", "ind"]')
flags.DEFINE_string(
    'compression', default=None, help='one of [None, "gzip", "lzf"]')

flags.DEFINE_string(
    'src_shape', default=None, help='one of ["pad", "jag", "ind", "cat"]')
flags.DEFINE_string(
    'src_compression', default=None, help='one of [None, "gzip", "lzf"]')
flags.DEFINE_string(
    'src_format', default=None,
    help='output format, one of '
         '[None, "file", "zip", "rle", "brle"]')

flags.DEFINE_boolean(
    'delete_src', default=False,
    help='if true, source data is delete (unless in is None)')


def safe_update(out, **added):
    for k, v in added.items():
        if v is not None:
            if k in out:
                raise ValueError('%s already in out' % k)
            out[k] = v


def main(_):
    from shapenet.core.voxels.config import get_config
    from shapenet.core.voxels.datasets import get_manager, convert
    from shapenet.core import to_cat_id
    config = get_config(FLAGS.voxel_dim, alt=FLAGS.alt)
    if FLAGS.cat is None:
        # from shapenet.r2n2 import get_cat_ids
        raise ValueError('Must provide at least one cat to convert.')
    if FLAGS.fill is not None:
        config = config.filled(FLAGS.fill)

    kwargs = dict(config=config, key=FLAGS.format)
    safe_update(kwargs, compression=FLAGS.compression, shape_key=FLAGS.shape)
    src_kwargs = dict()
    safe_update(
        src_kwargs, key=FLAGS.src_format, compression=FLAGS.src_compression,
        shape_key=FLAGS.src_shape)

    for cat in FLAGS.cat:
        dst = get_manager(cat_id=to_cat_id(cat), **kwargs)
        convert(
            dst, overwrite=FLAGS.overwrite, delete_src=FLAGS.delete_src,
            **src_kwargs)


app.run(main)
