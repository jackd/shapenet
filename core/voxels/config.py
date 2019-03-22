from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import six
from . import path
from .. import get_example_ids


class VoxelConfig(object):
    def __init__(
            self, voxel_dim=32, exact=True, dc=True, aw=True, c=False,
            v=False):
        self._voxel_dim = voxel_dim
        self._exact = exact
        self._dc = dc
        self._aw = aw
        self._c = c
        self._v = v
        self._voxel_id = get_voxel_id(
            voxel_dim, exact=exact, dc=dc, aw=aw, c=c, v=v)

    def filled(self, fill_alg=None):
        if fill_alg is None:
            return self
        else:
            from .filled import FilledVoxelConfig
            return FilledVoxelConfig(self, fill_alg)

    @staticmethod
    def from_id(voxel_id):
        kwargs = parse_voxel_id(voxel_id)
        fill_alg = kwargs.pop('fill_alg', None)
        return VoxelConfig(**kwargs).filled(fill_alg)

    @property
    def voxel_dim(self):
        return self._voxel_dim

    @property
    def exact(self):
        return self._exact

    @property
    def dc(self):
        return self._dc

    @property
    def aw(self):
        return self._aw

    @property
    def c(self):
        return self._c

    @property
    def v(self):
        return self._v

    @property
    def voxel_id(self):
        return self._voxel_id

    def get_binvox_subpath(self, cat_id, example_id):
        return path.get_binvox_subpath(cat_id, example_id)

    def get_binvox_path(self, cat_id, example_id):
        return os.path.join(
            self.root_dir, self.get_binvox_subpath(cat_id, example_id))

    @property
    def root_dir(self):
        return path.get_binvox_dir(self.voxel_id)

    def create_voxel_data(self, cat_id, example_ids=None, overwrite=False):
        from progress.bar import IncrementalBar
        from util3d.voxel.convert import obj_to_binvox
        from .. import objs
        if example_ids is None:
            example_ids = get_example_ids(cat_id)

        kwargs = dict(
            voxel_dim=self.voxel_dim,
            exact=self.exact,
            dc=self.dc,
            aw=self.aw,
            c=self.c,
            v=self.v,
            overwrite_original=True)

        path_ds = objs.get_extracted_obj_path_dataset(cat_id)
        bvd = self.get_binvox_path(cat_id, None)
        if not os.path.isdir(bvd):
            os.makedirs(bvd)

        with path_ds:
            print('Creating binvox voxel data')
            bar = IncrementalBar(max=len(example_ids))
            for example_id in example_ids:
                bar.next()
                binvox_path = self.get_binvox_path(cat_id, example_id)
                if overwrite or not os.path.isfile(binvox_path):
                    obj_path = path_ds[example_id]
                    obj_to_binvox(obj_path, binvox_path, **kwargs)
        bar.finish()

    def get_dataset(self, cat_id):
        from .datasets import get_dataset
        print(
            'Warning: voxel_config.get_dataset deprecated. '
            'Use voxels.datasets.get_dataset instead')
        return get_dataset(self, cat_id, key='zip')


def get_base_config(voxel_dim):
    return VoxelConfig(voxel_dim)


def get_alt_config(voxel_dim):
    return VoxelConfig(
        voxel_dim, exact=False, dc=False, aw=False, c=True, v=True)


def get_config(voxel_dim, alt=False):
    if alt:
        return get_alt_config(voxel_dim)
    else:
        return get_base_config(voxel_dim)


def get_voxel_id(
        voxel_dim=32, exact=True, dc=True, aw=True, c=False, v=False,
        fill=None):
    def bstr(b):
        return 't' if b else 'f'
    voxel_id = 'd%03d%s%s%s' % (voxel_dim, bstr(exact), bstr(dc), bstr(aw))
    if c:
        voxel_id = '%sc' % voxel_id
    if v:
        voxel_id = '%sv' % voxel_id
    if fill is not None:
        voxel_id = '%s_%s' % (voxel_id, fill)
    return voxel_id


default_voxel_id = get_voxel_id()


def split_id(voxel_id):
    parts = voxel_id.split('_')
    if len(parts) == 2:
        voxel_id, fill_alg = parts
    else:
        assert(len(parts) == 1)
        fill_alg = None
    return voxel_id, fill_alg


def parse_voxel_id(voxel_id):
    """Inverse function to `get_voxel_id`."""
    voxel_id, fill_alg = split_id(voxel_id)
    if not is_valid_voxel_id(voxel_id):
        raise ValueError('voxel_id %s not valid.' % voxel_id)
    kwargs = dict(
        voxel_dim=int(voxel_id[1:4]),
        exact=voxel_id[4] == 't',
        dc=voxel_id[5] == 't',
        aw=voxel_id[6] == 't',
    )
    rest = voxel_id[7:]
    if rest.startswith('c'):
        rest = rest[1:]
        kwargs['c'] = True
    if rest.startswith('v'):
        kwargs['v'] = True
        rest = rest[1:]
    assert(rest == '')
    if fill_alg is not None:
        kwargs['fill_alg'] = fill_alg
    return kwargs


def is_valid_voxel_id(voxel_id):
    voxel_id, fill_alg = split_id(voxel_id)
    if fill_alg is not None:
        from . import filled
        try:
            filled.check_valid_fill_alg(fill_alg)
        except ValueError:
            return False

    nc = len(voxel_id)
    if not isinstance(voxel_id, six.string_types) or 7 <= nc <= 9:
        return False
    if nc == 9 and nc[-2:] != 'cv':
        return False
    if nc == 8 and nc[-1] not in ('c', 'v'):
        return False
    try:
        int3 = int(voxel_id[1:4])
    except ValueError:
        return False
    if int3 <= 0:
        return False
    return voxel_id[0] == 'd' and all(s in ('t', 'f') for s in voxel_id[4:])
