import os
import zipfile
import path


class VoxelConfig(object):
    def __init__(self, voxel_dim=32, exact=True, dc=True, aw=True):
        self._voxel_dim = voxel_dim
        self._exact = exact
        self._dc = dc
        self._aw = aw
        self._voxel_id = path.get_voxel_id(
            voxel_dim, exact=exact, dc=dc, aw=aw)

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

    def get_zip_file(self, cat_id, mode='r'):
        return zipfile.ZipFile(self.get_zip_path(cat_id), mode)

    def create_voxel_data(self, cat_id, example_ids=None, overwrite=False):
        import shutil
        from progress.bar import IncrementalBar
        from util3d.voxel.convert import obj_to_binvox
        from shapenet.core.path import get_zip_file, get_obj_subpath, \
            get_example_subdir
        from shapenet.core.voxels.path import get_binvox_path
        if example_ids is None:
            from shapenet.core import get_example_ids
            example_ids = get_example_ids(cat_id)
        tmp_dir = '/tmp'

        kwargs = dict(
            voxel_dim=self.voxel_dim,
            exact=self.exact,
            dc=self.dc,
            aw=self.aw)
        voxel_id = self.voxel_id

        print('Creating voxel data.')
        with get_zip_file(cat_id) as zf:
            bar = IncrementalBar(max=len(example_ids))
            for example_id in example_ids:
                bar.next()
                binvox_path = get_binvox_path(voxel_id, cat_id, example_id)
                if os.path.isfile(binvox_path):
                    if overwrite:
                        os.remove(binvox_path)
                    else:
                        continue
                subdir = os.path.dirname(binvox_path)
                if not os.path.isdir(subdir):
                    os.makedirs(subdir)
                subpath = get_obj_subpath(cat_id, example_id)
                zf.extract(subpath, tmp_dir)
                obj_path = os.path.join(tmp_dir, subpath)
                extraction_dir = os.path.join(
                    tmp_dir, get_example_subdir(cat_id, example_id))
                try:
                    obj_to_binvox(obj_path, binvox_path, **kwargs)
                except IOError:
                    print('Error generating %s/%s' % (cat_id, example_id))
                shutil.rmtree(extraction_dir)
            bar.finish()

    def create_zip_file(self, cat_id, example_ids=None, overwrite=False):
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

    def get_dataset(self, cat_id, mode='r'):
        path = self.get_zip_path(cat_id)
        if not os.path.isfile(path):
            self.create_voxel_data(cat_id)
            self.create_zip_file(cat_id)
        assert(os.path.isfile(path))
        return self._get_dataset(cat_id, mode)
