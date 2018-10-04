from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import tarfile
import os
import collections
import logging
from .path import data_dir, get_renderings_subpath, get_binvox_subpath


_logger = logging.getLogger(__name__)
renderings_path = os.path.join(data_dir, 'ShapeNetRendering.tgz')
binvox_path = os.path.join(data_dir, 'ShapeNetVox32.tgz')

binvox_url = 'ftp://cs.stanford.edu/cs/cvgl/ShapeNetVox32.tgz'
renderings_url = 'ftp://cs.stanford.edu/cs/cvgl/ShapeNetRendering.tgz'


class ArchiveManager(object):
    def __init__(self, url, path, mode='r:gz'):
        self._path = path
        self._mode = mode
        self._url = url
        self._file = None
        self._members = None

    @property
    def path(self):
        return self._path

    @property
    def url(self):
        return self._url

    @property
    def mode(self):
        return self._mode

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def open(self):
        if not os.path.isfile(self._path):
            self.download()
        assert(os.path.isfile(self._path))
        self._file = tarfile.open(self._path, self._mode)
        self._members = {m.name: m for m in self._file.getmembers()}

    def close(self):
        self._file = file
        self._members = None

    def extract(self):
        _logger.info('Extracting contents of %s' % self.path)
        self._file.extractall(path=data_dir)

    @property
    def is_open(self):
        return not self.is_closed

    @property
    def is_closed(self):
        return self._file is None

    def load_subpath(self, subpath):
        return self._file.extractfile(self._members[subpath])

    def download(self):
        import wget
        path = self.path
        if os.path.isfile(path):
            _logger.info(
                'Data already present at %s. Skipping download' % path)
        else:
            url = self.url
            _logger.info('Downloading from %s' % url)
            wget.download(self.url, out=path)


class BinvoxManager(ArchiveManager):
    def __init__(self):
        super(BinvoxManager, self).__init__(binvox_url, binvox_path, 'r:gz')
        self._cat_ids = None
        self._example_ids = {}

    def __getitem__(self, args):
        cat_id, example_id = args
        return self.load(cat_id, example_id)

    def load(self, cat_id, example_id):
        from util3d.voxel.binvox import Voxels
        fp = self.load_subpath(get_binvox_subpath(cat_id, example_id))
        vox = Voxels.from_file(fp)
        return vox

    def get_example_ids(self):
        example_ids = {}
        for name in self._members:
            args = name.split('/')
            if args[-1].endswith('.binvox'):
                cat_id, example_id = args[1:3]
                example_ids.setdefault(cat_id, []).append(example_id)
        return example_ids


# https://github.com/chrischoy/3D-R2N2/issues/12
meta = collections.namedtuple('RenderingMeta', [
    'azimuth',
    'elevation',
    'in_plane_rotation',
    'distance',
    'field_of_view',
])


def parse_meta_line(line):
    return tuple(float(x) for x in line.rstrip().split(' '))


class RenderingsManager(ArchiveManager):
    def __init__(self):
        super(RenderingsManager, self).__init__(
            renderings_url, renderings_path, 'r:gz')
        self._cat_ids = None
        self._example_ids = {}

    def __getitem__(self, args):
        cat_id, example_id, view_index = args
        return self.load(cat_id, example_id, view_index)

    def load(self, cat_id, example_id, view_index):
        from PIL import Image
        fp = self.load_subpath(get_renderings_subpath(
            cat_id, example_id, view_index))
        return Image.open(fp)

    def get_meta_lines(self, cat_id, example_id):
        meta_path = get_renderings_subpath(
            cat_id, example_id, 'rendering_metadata.txt')
        fp = self.load_subpath(meta_path)
        lines = fp.readlines()
        return tuple(line for line in lines if len(lines) > 0)

    def get_metas(self, cat_id, example_id):
        lines = self.get_meta_lines(cat_id, example_id)
        return tuple(parse_meta_line(line) for line in lines)
