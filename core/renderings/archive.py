"""Uniform interface for zip/tar archives."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import zipfile
import tarfile


class Archive(object):
    def add(self, src, dst):
        raise NotImplementedError('Abstract method')

    def get_names(self):
        raise NotImplementedError('Abstract method')

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def open(self):
        raise NotImplementedError('Abstract method')

    def close(self):
        raise NotImplementedError('Abstract method')


class ArchiveBase(Archive):
    def __init__(self, path, mode):
        self._path = path
        self._mode = mode
        self._file = None

    def get_open_file(self):
        raise NotImplementedError('Abstract method')

    def __str__(self):
        return '<Archive: %s>' % self._path

    def __repr__(self):
        return self.__str__()

    def close(self):
        self._file = None

    def open(self):
        self._file = self.get_open_file(self._path, self._mode)


class ZipArchive(ArchiveBase):
    def get_open_file(self, path, mode):
        return zipfile.ZipFile(
            path, mode, zipfile.ZIP_DEFLATED, allowZip64=True)

    def add(self, src, dst):
        self._file.write(src, dst)

    def get_names(self):
        return self._file.namelist()


class TarArchive(ArchiveBase):
    def get_open_file(self, path, mode):
        return tarfile.open(path, mode)

    def add(self, src, dst):
        self._file.add(src, dst)

    def get_names(self):
        return (member.name for member in self._file.getmembers())


def get_archive(path, mode='r'):
    ext = os.path.splitext(path)[1]
    if ext == '.zip':
        return ZipArchive(path, mode)
    elif ext == '.tar':
        return TarArchive(path, mode)
    else:
        raise KeyError('Unrecognized archive extension "%s"' % ext)
