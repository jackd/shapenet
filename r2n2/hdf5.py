from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import logging
import numpy as np
import h5py
from progress.bar import IncrementalBar
from PIL import Image
from . import path
from . import tgz

hdf5_dir = os.path.join(path.data_dir, 'hdf5')
# hdf5_dir = os.path.join(path.data_dir, '..', 'scripts')
_logger = logging.getLogger(__name__)
n_renderings = 24
voxel_dim = 32
meta_keys = (
    'azimuth', 'elevation', 'in_plane_rotation', 'distance', 'field_of_view')
_meta_indices = {k: i for i, k in enumerate(meta_keys)}


def meta_index(key):
    return _meta_indices[key]


def get_hdf5_path(cat_id):
    return os.path.join(hdf5_dir, '%s.hdf5' % cat_id)


def get_hdf5_data(cat_id, mode='r'):
    return h5py.File(get_hdf5_path(cat_id), mode)


def numpy_to_buffer(data):
    import io
    import numpy as np
    if not isinstance(data, np.ndarray):
        raise ValueError('data must be a numpy array')
    return io.BytesIO(data)


def numpy_to_image(data):
    return Image.open(numpy_to_buffer(data))


def buffer_to_numpy(fp, dtype=np.uint8):
    import numpy as np
    return np.fromstring(fp.read(), dtype=dtype)


def _ensure_extracted():
    if not os.path.isdir(path.get_renderings_path()):
        with tgz.RenderingsManager() as rm:
            rm.extractall()


def get_cat_ids():
    return tuple(fn[:-5] for fn in os.listdir(hdf5_dir))


class Converter(object):
    def __init__(self, cat_id, example_ids=None, mode='r'):
        if example_ids is None:
            with tgz.BinvoxManager() as bm:
                example_ids = bm.get_example_ids()[cat_id]
        self._cat_id = cat_id
        self._example_ids = sorted(example_ids)
        self._mode = mode
        self._file = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def open(self):
        p = get_hdf5_path(self._cat_id)
        d = os.path.dirname(p)
        if not os.path.isdir(d):
            os.makedirs(d)
        self._file = h5py.File(p, self._mode)

    def close(self):
        self._file.close()
        self._file = None

    def setup(self, overwrite=False):
        _logger.info('Setting up hdf5.%s' % self._cat_id)
        vlen_dtype = h5py.special_dtype(vlen=np.dtype(np.uint8))
        n = len(self._example_ids)
        if overwrite:
            for k in ('example_ids', 'rle_data', 'renderings', 'meta'):
                del self._file[k]

        if 'example_ids' not in self._file:
            id_group = self._file.create_dataset(
                'example_ids', shape=(n,), dtype='S32')
            for i, e in enumerate(self._example_ids):
                id_group[i] = e
        else:
            assert(len(self._file['example_ids']) == n)
        self._file.require_dataset(
            'rle_data', shape=(n,), dtype=vlen_dtype)
        self._file.require_dataset(
            'renderings', shape=(n, n_renderings), dtype=vlen_dtype)
        self._file.require_dataset(
            'meta', shape=(n, n_renderings, 5), dtype=np.float32)

    def convert_voxels(self, overwrite=False):
        _logger.info('Converting voxel data for hdf5.%s' % self._cat_id)
        group = self._file['rle_data']
        with tgz.BinvoxManager() as bm:
            bar = IncrementalBar(max=len(self._example_ids))
            for i, example_id in enumerate(self._example_ids):
                if overwrite or len(group[i]) == 0:
                    group[i] = bm.load(self._cat_id, example_id).rle_data()
                bar.next()
            bar.finish()

    def convert_renderings(self, overwrite=False):
        _logger.info('Converting voxel data for hdf5.%s' % self._cat_id)
        group = self._file['renderings']
        cat_id = self._cat_id
        _ensure_extracted()
        bar = IncrementalBar(max=len(self._example_ids))
        for i, example_id in enumerate(self._example_ids):
            for j in range(n_renderings):
                if overwrite or len(group[i, j]) == 0:
                    p = path.get_renderings_path(cat_id, example_id, j)
                    with open(p, 'r') as fp:
                        group[i, j] = buffer_to_numpy(fp)
            bar.next()
        bar.finish()

    def convert_meta(self, overwrite=False):
        group = self._file['meta']
        _ensure_extracted()
        cat_id = self._cat_id
        bar = IncrementalBar(max=len(self._example_ids))
        for i, example_id in enumerate(self._example_ids):
            if overwrite or np.all(group[i] == 0):
                p = path.get_renderings_path(
                    cat_id, example_id, 'rendering_metadata.txt')
                with open(p, 'r') as fp:
                    lines = [line for line in fp.readlines() if len(line) > 1]
                meta = [
                    [float(n) for n in line.rstrip().split(' ')]
                    for line in lines]
                group[i] = np.array(meta, dtype=np.float32)
            bar.next()
        bar.finish()

    def convert(
            self, setup=True, voxels=True, meta=True, renderings=True,
            overwrite=False):
        if setup:
            self.setup(overwrite=overwrite)
        if voxels:
            self.convert_voxels(overwrite=overwrite)
        if meta:
            self.convert_meta(overwrite=overwrite)
        if renderings:
            self.convert_renderings(overwrite=overwrite)


class Hdf5Manager(object):
    def __init__(self, cat_id):
        self._file = None
        self._cat_id = cat_id

    @property
    def cat_id(self):
        return self._cat_id

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        self._file.close()
        self._file = None

    @property
    def meta_group(self):
        return self._file['meta']

    @property
    def renderings_group(self):
        return self._file['renderings']

    @property
    def rle_group(self):
        return self._file['rle_data']

    def open(self):
        path = get_hdf5_path(self._cat_id)
        if not os.path.isfile(path):
            _logger.info(
                'No hdf5 data found for category %s. Converting...'
                % self._cat_id)
            with self.get_converter(mode='a') as converter:
                converter.convert()
        self._file = h5py.File(path, mode='r')

    def get_converter(self, mode='a'):
        return Converter(self._cat_id, 'a')

    def get_voxels(self, example_index):
        from util3d.voxel.binvox import RleVoxels
        return RleVoxels(self.get_rle_data(example_index), (32,)*3)

    def get_rle_data(self, example_index):
        return np.array(self._file['rle_data'][example_index])

    def get_rendering(self, example_index, view_index):
        return numpy_to_image(
            np.array(self._file['renderings'][example_index, view_index]))

    def get_meta(self, example_index, view_index):
        return np.array(self._file['meta'][example_index, view_index])

    def get_example_ids(self):
        return np.array(self._file['example_ids'], dtype='S32')
