from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import dids.core as c
from dids.file_io.hdf5 import Hdf5Resource


class ConcatenatedDataset(c.DependentResource, c.Dataset):
    def __init__(self, path, starts_key='starts', values_key='values'):
        c.DependentResource.__init__(Hdf5Resource(path))
        self._starts_key = starts_key
        self._values_key = values_key

    def _open_self(self):
        c.DependentResource._open_self(self)
        self._starts = self._parent._base[self._starts_key]
        self._values = self._parent._base[self._values_key]

    def __contains__(self, key):
        return isinstance(key, int) and 0 <= key < self._len

    def __len__(self):
        return self._len

    def __keys__(self):
        return range(self._len)

    def __getitem__(self, key):
        start, end = self._starts[key: key + 2]
        values = self._values[start:end]
        return values
