#!/usr/bin/python

"""
Script for creating/converting voxel data formats.

Example usage:
./create_dataset.py --cat=car,plane --voxel_dim=128 \
    --format=rle --overwrite=True --compression=gzip --pad=True
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
    'format', default=None,
    help='input format, one of '
         '[None, "file", "zip", "rle", "brle"]')
flags.DEFINE_boolean(
    'pad', default=None,
    help='whether or not to pad data for rle/brle formats')
flags.DEFINE_string(
    'compression', default=None, help='one of ["gzip", "lzf"]')

flags.DEFINE_boolean(
    'src_pad', default=None, help='whether or not to use padded src')
flags.DEFINE_boolean(
    'src_compression', default=None, help='one of ["gzip", "lzf"]')
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
    from shapenet.core import cat_desc_to_id
    config = get_config(FLAGS.voxel_dim, alt=FLAGS.alt)
    if FLAGS.cat is None:
        raise ValueError('Must provide at least one cat to convert.')
    if FLAGS.fill is not None:
        config = config.filled(FLAGS.fill)

    kwargs = dict(config=config, key=FLAGS.format)
    safe_update(kwargs, compression=FLAGS.compression, pad=FLAGS.pad)
    src_kwargs = dict(key=FLAGS.src_format)
    safe_update(
        src_kwargs, compression=FLAGS.src_compression, pad=FLAGS.src_pad)

    for cat in FLAGS.cat:
        dst = get_manager(cat_id=cat_desc_to_id(cat), **kwargs)
        convert(
            dst, overwrite=FLAGS.overwrite, delete_src=FLAGS.delete_src,
            **src_kwargs)


app.run(main)
