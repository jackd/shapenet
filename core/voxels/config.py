from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import zipfile
import numpy as np
from . import path
from .. import get_example_ids
import util3d.voxel.rle as rle


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
        self._voxel_id = path.get_voxel_id(
            voxel_dim, exact=exact, dc=dc, aw=aw, c=c, v=v)

    def filled(self, fill_alg=None):
        from .filled import FilledVoxelConfig
        return FilledVoxelConfig(self, fill_alg)

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

    def get_zip_path(self, cat_id):
        return os.path.join(self.root_dir, '%s.zip' % cat_id)

    def get_hdf5_path(self, cat_id):
        return os.path.join(self.root_dir, '%s.hdf5' % cat_id)

    def get_zip_file(self, cat_id, mode='r'):
        return zipfile.ZipFile(self.get_zip_path(cat_id), mode)

    def create_voxel_data(self, cat_id, example_ids=None, overwrite=False):
        import shutil
        from progress.bar import IncrementalBar
        from util3d.voxel.convert import obj_to_binvox
        from .. import path as core_path
        if example_ids is None:
            example_ids = get_example_ids(cat_id)
        tmp_dir = '/tmp'

        kwargs = dict(
            voxel_dim=self.voxel_dim,
            exact=self.exact,
            dc=self.dc,
            aw=self.aw,
            c=self.c,
            v=self.v)

        with core_path.get_zip_file(cat_id) as zf:
            bar = IncrementalBar(max=len(example_ids))
            for example_id in example_ids:
                bar.next()
                binvox_path = self.get_binvox_path(cat_id, example_id)
                if os.path.isfile(binvox_path):
                    if overwrite:
                        os.remove(binvox_path)
                    else:
                        continue
                subdir = os.path.dirname(binvox_path)
                if not os.path.isdir(subdir):
                    os.makedirs(subdir)
                subpath = core_path.get_obj_subpath(cat_id, example_id)
                zf.extract(subpath, tmp_dir)
                obj_path = os.path.join(tmp_dir, subpath)
                extraction_dir = os.path.join(
                    tmp_dir, core_path.get_example_subdir(cat_id, example_id))
                try:
                    obj_to_binvox(obj_path, binvox_path, **kwargs)
                except IOError:
                    print('Error generating %s/%s' % (cat_id, example_id))
                shutil.rmtree(extraction_dir)
            bar.finish()

    def create_zip_file(
            self, cat_id, example_ids=None, overwrite=False, delete_src=False):
        if example_ids is None or len(example_ids) == 0:
            path = self.get_binvox_path(cat_id, None)
            example_ids = (e[:-7] for e in os.listdir(path))
        with zipfile.ZipFile(self.get_zip_path(cat_id), 'a') as zf:
            if not overwrite:
                namelist = set(zf.namelist())
            for example_id in example_ids:
                dst = self.get_binvox_subpath(cat_id, example_id)
                if not overwrite and dst in namelist:
                    continue
                src = self.get_binvox_path(cat_id, example_id)
                zf.write(src, dst)
        if delete_src:
            import shutil
            shutil.rmtree(self.get_binvox_path(cat_id, None))

    def _create_hdf5(self, cat_id, load_fn):
        import h5py
        from .. import get_example_ids

        from progress.bar import IncrementalBar
        example_ids = get_example_ids(cat_id)
        n = len(example_ids)
        dtype = h5py.special_dtype(vlen=np.dtype(np.uint8))
        path = self.get_hdf5_path(cat_id)
        print('Creating hdf5 data at %s' % path)
        with h5py.File(path, 'a') as root:
            rle_data = root.require_dataset(
                'rle_data', dtype=dtype, shape=(n,))
            bar = IncrementalBar(max=n)
            for i, example_id in enumerate(example_ids):
                rle_data[i] = load_fn(example_id)
                bar.next()
            bar.finish()

    def create_hdf5_data(self, cat_id, delete_src=False):
        from util3d.voxel.binvox import Voxels

        def load_fn(example_id):
            src_path = self.get_binvox_path(cat_id, example_id)
            if not os.path.isfile(src_path):
                return rle.zeros(self.voxel_dim**3)
            try:
                vox = Voxels.from_path(src_path)
            except IOError:
                self.create_voxel_data(cat_id, [example_id])
                try:
                    vox = Voxels.from_path(src_path)
                except IOError:
                    print('Error with example %s' % cat_id)
                    return rle.zeros(self.voxel_dim**3)
            return vox.rle_data()
        self._create_hdf5(cat_id, load_fn)
        if delete_src:
            import shutil
            shutil.rmtree(self.get_binvox_path(cat_id, None))

    def create_hdf5_data_from_zip(self, cat_id, delete_src=False):
        from util3d.voxel.binvox import Voxels
        with self.get_dataset(cat_id) as ds:
            def load_fn(example_id):
                if example_id in ds:
                    return ds[example_id].rle_data()
                else:
                    self.create_voxel_data(cat_id, [example_id])
                    p = self.get_binvox_path(cat_id, example_id)
                    if not os.path.isfile(p):
                        print('***')
                        print('Error with %s - %s' % (cat_id, example_id))
                        print('***')
                        return rle.zeros(self.voxel_dim**3)
                    rle_data = Voxels.from_path(p).rle_data()
                    if delete_src:
                        os.remove(p)
                    return rle_data

            self._create_hdf5(cat_id, load_fn)
        if delete_src:
            os.remove(self.get_zip_path(cat_id))

    def _get_dataset(self, cat_id, mode='r'):
        from dids.file_io.zip_file_dataset import ZipFileDataset
        from util3d.voxel.binvox import Voxels

        def key_fn(example_id):
            return self.get_binvox_subpath(cat_id, example_id)

        def inverse_key_fn(path):
            subpaths = path.split('/')
            if len(subpaths) == 2:
                fn = subpaths[-1]
                if len(fn) > 7 and fn[-7:] == '.binvox':
                    return fn[:-7]
            return None

        dataset = ZipFileDataset(self.get_zip_path(cat_id), mode)
        dataset = dataset.map(Voxels.from_file)
        dataset = dataset.map_keys(key_fn, inverse_key_fn)
        return dataset

    def get_zip_dataset(self, cat_id, mode='r'):
        path = self.get_zip_path(cat_id)
        if not os.path.isfile(path):
            self.create_voxel_data(cat_id)
            self.create_zip_file(cat_id)
        assert(os.path.isfile(path))
        return self._get_dataset(cat_id, mode)

    def get_dataset(self, cat_id, src=None, mode='r'):
        if src is None:
            if os.path.isfile(self.get_hdf5_path(cat_id)):
                src = 'hdf5'
            elif os.path.isfile(self.get_zip_path(cat_id)):
                src = 'zip'
            else:
                src = 'hdf5'
        if src == 'hdf5':
            return self.get_hdf5_dataset(cat_id, mode)
        elif src == 'zip':
            return self.get_zip_dataset(cat_id, mode)
        else:
            raise ValueError(
                'Unrecognized src "%s": must be one of ("zip", "hdf5")' % src)

    def _get_hdf5_dataset(self, cat_id, mode='r', id_keys=True):
        from dids.file_io.hdf5 import Hdf5Dataset, Hdf5ArrayDataset
        from util3d.voxel.binvox import RleVoxels
        base = Hdf5Dataset(self.get_hdf5_path(cat_id))
        ds = Hdf5ArrayDataset(base, 'rle_data')
        example_ids = get_example_ids(cat_id)
        indices = {k: i for i, k in enumerate(example_ids)}

        dims = (self.voxel_dim,)*3
        ds = ds.map(lambda data: RleVoxels(data, dims))
        if id_keys:
            ds = ds.map_keys(
                lambda example_id: indices[example_id],
                lambda index: example_ids[index])
        return ds

    def get_hdf5_dataset(self, cat_id, mode='r', id_keys=True):
        path = self.get_hdf5_path(cat_id)
        if not os.path.isfile(path):
            if os.path.isfile(self.get_zip_path(cat_id)):
                self.create_hdf5_data_from_zip(cat_id)
            else:
                self.create_voxel_data(cat_id)
                self.create_hdf5_data(cat_id)
        assert(os.path.isfile(path))
        return self._get_hdf5_dataset(cat_id, mode=mode, id_keys=id_keys)


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
