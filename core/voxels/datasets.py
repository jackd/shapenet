from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import os
import shutil
import numpy as np
from util3d.voxel import binvox as bv
from shapenet.core import get_example_ids


def _as_readable(writing_fn):
    import io
    fp = io.BytesIO()
    writing_fn(fp)
    fp.seek(0)
    return fp


def _map_binvox_dataset(dataset, cat_id, id_keys=True):
    dataset = dataset.map(
        bv.Voxels.from_file,
        inverse_map_fn=lambda vox: _as_readable(vox.save_to_file))
    if id_keys:
        dataset = dataset.map_keys(
            lambda x: '%s.binvox' % x,
            lambda x: x[:-7])
    else:
        example_ids = get_example_ids(cat_id)
        indices = {k: i for i, k in enumerate(example_ids)}
        dataset = dataset.map_keys(
            lambda i: '%s.binvox' % (example_ids[i]),
            lambda k: indices[k[:-7]])
    return dataset


class DatasetManager(object):
    def __init__(self, config, cat_id):
        self._config = config
        self._cat_id = cat_id

    @property
    def config(self):
        return self._config

    @property
    def cat_id(self):
        return self._cat_id

    @property
    def format_key(self):
        raise NotImplementedError('Abstract property')

    def get_manager(self, key=None, **kwargs):
        return get_manager(self.config, self.cat_id, key, **kwargs)

    def create_from(self, src=None, overwrite=False):
        if src is None:
            src = self.get_manager('file')
        with src.get_dataset(id_keys=False) as src:
            with self._get_dataset(id_keys=False, mode='a') as dst:
                print(
                    'Creating voxel rle dataset from src: %s' % src.format_key)
                dst.save_dataset(
                    src, overwrite=overwrite, show_progress=True)

    def delete(self):
        raise NotImplementedError('Abstract method')

    def _get_dataset(self, id_keys, mode='r'):
        raise NotImplementedError('Abstract method')

    def has_dataset(self):
        raise NotImplementedError('Abstract method')

    def get_dataset(self, id_keys=True):
        if not self.has_dataset():
            self.create_from(None)
        return self._get_dataset(id_keys, mode='r')


class BinvoxManager(DatasetManager):
    def create_from(self, src, overwrite=False):
        if src is None:
            self.config.create_voxel_data(self.cat_id, overwrite=overwrite)
        else:
            return super(BinvoxManager, self).create_from(
                src, overwrite=overwrite)

    def has_dataset(self):
        dd = self.data_dir
        return os.path.isdir(dd) and len(
            os.listdir(dd)) == len(get_example_ids(self.cat_id))

    @property
    def data_dir(self):
        return self.config.get_binvox_path(self.cat_id, None)

    def delete(self):
        d = self.data_dir
        print('Deleting binvox file data from %s' % d)
        shutil.rmtree(d)

    def _get_dataset(self, id_keys=True, mode='r'):
        from dids.file_io.file_dataset import FileDataset
        dd = self.data_dir
        if not os.path.isdir(dd):
            os.makedirs(dd)
        dataset = FileDataset(dd, mode=mode)
        return _map_binvox_dataset(dataset, self.cat_id, id_keys=id_keys)

    @property
    def format_key(self):
        return 'file'


class ZippedBinvoxManager(DatasetManager):
    def create_from(self, src, overwrite=False):
        if src is None:
            src = self.get_manager('file')
        elif src.format_key != 'file':
            raise ValueError('Can only create ZippedBinvox data from "file"')
        path = self.path
        if os.path.isfile(path) and not overwrite:
            raise NotImplementedError()
        shutil.make_archive(path[:-4], 'zip', src.data_dir)

    @property
    def path(self):
        return os.path.join(self.config.root_dir, '%s.zip' % self.cat_id)

    def has_dataset(self):
        return os.path.isfile(self.path)

    def delete(self):
        path = self.path
        print('Deleting zipped binvox data from %s' % path)
        os.remove(path)

    def _get_dataset(self, id_keys=True, mode='r'):
        from dids.file_io.zip_file_dataset import ZipFileDataset
        dataset = ZipFileDataset(self.path, mode=mode)
        return _map_binvox_dataset(dataset, self.cat_id, id_keys)

    @property
    def format_key(self):
        return 'zip'


class Hdf5Manager(DatasetManager):
    def __init__(self, config, cat_id, encoder, compression='gzip'):
        super(Hdf5Manager, self).__init__(config, cat_id)
        if isinstance(compression, (str, unicode)):
            compression = compression.lower()
            if compression == 'none':
                compression = None
        self._compression = compression
        self._encoder = as_encoder(encoder)

    def _get_default_src(self):
        src = self.get_manager('zip')
        if not src.has_dataset():
            src = self.get_manager('file')
        return src

    @property
    def encoder(self):
        return self._encoder

    @property
    def compression(self):
        return self._compression

    @property
    def format_key(self):
        comp = self.compression
        return self.encoder.key if comp is None else \
            '%s-%s' % (self.encoder.key, comp)

    def delete(self):
        print('Deleting %s hdf5 data' % self.format_key)
        os.remove(self.path)

    @property
    def path(self):
        return os.path.join(
            self.config.root_dir, '%s-%s.hdf5' %
            (self.cat_id, self.format_key))

    def has_dataset(self):
        return os.path.isfile(self.path)

    @property
    def _group_name(self):
        return '%s_data' % self.format_key

    def _get_dataset(self, id_keys=True, mode='r'):
        from dids.file_io.hdf5 import Hdf5Dataset, Hdf5ArrayDataset
        parent = Hdf5Dataset(self.path, mode=mode)
        dataset = Hdf5ArrayDataset(parent, self._group_name)
        dims = (self.config.voxel_dim,) * 3
        decode = self.encoder.from_numpy
        dataset = dataset.map(lambda x: decode(np.array(x), dims))

        if id_keys:
            example_ids = get_example_ids(self.cat_id)
            indices = {k: i for i, k in enumerate(example_ids)}
            dataset = dataset.map_keys(
                lambda k: indices[k],
                lambda i: example_ids[i])
        return dataset


class VlenHdf5Manager(Hdf5Manager):

    def create_from(self, src=None, overwrite=False):
        import h5py
        from progress.bar import IncrementalBar
        if src is None:
            src = self._get_default_src()
        with src.get_dataset(id_keys=True) as src:
            example_ids = get_example_ids(self.cat_id)
            n = len(example_ids)
            dtype = h5py.special_dtype(vlen=np.dtype(np.uint8))
            with h5py.File(self.path, 'a') as dst:
                dst = dst.require_dataset(
                    self._group_name, dtype=dtype, shape=(n,),
                    compression=self.compression)
                print('Saving data to %s' % self.path)
                bar = IncrementalBar(max=n)
                encode = self.encoder.to_numpy
                for i, example_id in enumerate(example_ids):
                    if example_id in src and (overwrite or len(dst[i]) == 0):
                        dst[i] = encode(src[example_id])
                    bar.next()
                bar.finish()


class PaddedHdf5Manager(Hdf5Manager):
    @property
    def format_key(self):
        comp = self.compression
        if comp is None:
            return '%s-pad' % (self.encoder.key)
        else:
            return '%s-pad-%s' % (self.encoder.key, comp)

    def _get_default_src(self):
        src = self.get_manager(
            'hdf5', encoder=self.encoder, compression=self.compression)
        if src.has_dataset():
            return src
        for compression in ('lzf', 'gzip', None):
            if compression != self.compression:
                src = self.get_manager(
                    'hdf5', encoder=self.encoder, compression=compression)
                if src.has_dataset():
                    return src

        return super(PaddedHdf5Manager, self)._get_default_src()

    def create_from(self, src=None, overwrite=False):
        import h5py
        from progress.bar import IncrementalBar
        if src is None:
            src = self._get_default_src()
        with src.get_dataset(id_keys=True) as src:
            example_ids = get_example_ids(self.cat_id)
            n = len(example_ids)
            values = []
            print('Getting pre-padded encodings for %s...' % self.format_key)
            bar = IncrementalBar(max=n)
            encode = self.encoder.to_numpy
            for i in example_ids:
                val = encode(src[i])
                values.append(val)
                bar.next()
            bar.finish()
            m = max(len(v) for v in values)
            print('Saving...')
            with h5py.File(self.path, 'a') as dst:
                dst = dst.require_dataset(
                    self._group_name, dtype=np.uint8, shape=(n, m),
                    compression=self.compression)
                print('Saving data to %s' % self.path)
                for i, val in enumerate(values):
                    dst[i, :len(val)] = val


class Encoder(object):
    def to_numpy(self, voxels):
        raise NotImplementedError('Abstract method')

    def from_numpy(self, encoding, dims):
        raise NotImplementedError('Abstract method')

    @property
    def key(self):
        raise NotImplementedError('Abstract property')

    def tostring(self, voxels):
        return self.to_numpy(voxels).tostring()

    def fromstring(self, bin, dims):
        return self.from_numpy(np.fromstring(bin, dtype=np.uint8), dims)

    def to_file(self, fp, voxels):
        fp.write(self.tostring(voxels))

    def from_file(self, fp, dims):
        return self.fromstring(fp.read(), dims)


class RleEncoder(Encoder):
    def to_numpy(self, vox):
        return vox.rle_data()

    def from_numpy(self, encoding, dims):
        return bv.RleVoxels(encoding, dims)

    @property
    def key(self):
        return 'rle'


class BrleEncoder(Encoder):
    def to_numpy(self, vox):
        return vox.brle_data()

    def from_numpy(self, encoding, dims):
        return bv.BrleVoxels(encoding, dims)

    @property
    def key(self):
        return 'brle'


_encoders = {
    'rle': RleEncoder,
    'brle': BrleEncoder,
}


def as_encoder(encoder):
    if isinstance(encoder, Encoder):
        return encoder
    elif isinstance(encoder, (str, unicode)):
        return _encoders[encoder]()
    else:
        raise ValueError('Unrecognized encoder %s' % str(encoder))


_save_fns = {
    'rle': lambda v: v.rle_data(),
    'brle': lambda v: v.brle_data(),
}


_load_fns = {
    'rle': bv.RleVoxels,
    'brle': bv.BrleVoxels,
}


def get_hdf5_manager(
        config, cat_id, encoder='rle', pad=True, compression='gzip'):
    fn = PaddedHdf5Manager if pad else VlenHdf5Manager
    return fn(config, cat_id, encoder=as_encoder(encoder),
              compression=compression)


get_rle_manager = functools.partial(get_hdf5_manager, encoder='rle')
get_brle_manager = functools.partial(get_hdf5_manager, encoder='brle')


_manager_factory = {
    'file': BinvoxManager,
    'zip': ZippedBinvoxManager,
    'hdf5': get_hdf5_manager,
    'rle': get_rle_manager,
    'brle': get_brle_manager,
}


def get_manager(config, cat_id, key='file', **kwargs):
    return _manager_factory[key](config, cat_id, **kwargs)


def get_dataset(config, cat_id, id_keys=True, key='file', **kwargs):
    return get_manager(
        config, cat_id, key, **kwargs).get_dataset(id_keys)


def convert(dst, overwrite=False, delete_src=False, **src_kwargs):
    src = dst.get_manager(**src_kwargs)
    dst.create_from(src, overwrite=overwrite)
    if delete_src:
        src.delete()


def get_manager_from_filename(config, fn):
    base_and_ext = fn.split('.')
    if len(base_and_ext) == 1:
        return get_manager(config, fn, key='file')
    base, ext = base_and_ext
    if ext == 'zip':
        cat_id = base
        return get_manager(config, cat_id, key='zip')
    elif ext == 'hdf5':
        base = base.split('-')
        kwargs = dict(config=config, cat_id=base[0])
        if len(base) == 2:
            cat_id = base[0]
            if base[1] == 'pad':
                return get_hdf5_manager(compression=None, pad=True, **kwargs)
            else:
                return get_hdf5_manager(
                    compression=base[1], pad=False, **kwargs)
        elif len(base) == 3:
            assert(base[1] == 'pad')
            return get_hdf5_manager(compression=base[2], pad=True, **kwargs)

    raise ValueError('Unrecognized filename %s' % fn)
