#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np
from progress.bar import IncrementalBar
from shapenet.r2n2.hdf5 import get_hdf5_path, get_cat_ids, n_renderings
import h5py


def fix(cat_id):
    p0 = get_hdf5_path(cat_id)
    temp_p = os.path.realpath(os.path.join(
        os.path.dirname(__file__), os.path.split(p0)[1]))
    vlen_dtype = h5py.special_dtype(vlen=np.dtype(np.uint8))
    with h5py.File(p0, 'r') as src:
        example_ids = tuple(src['example_ids'])
        indices = {k: i for i, k in enumerate(example_ids)}
        example_ids = np.array(sorted(example_ids), dtype='S32')
        n = len(example_ids)
        with h5py.File(temp_p, 'w') as dst:
            dst.create_dataset('example_ids', data=example_ids)
            rle_data = dst.create_dataset(
                'rle_data', shape=(n,), dtype=vlen_dtype)
            meta = dst.create_dataset('meta', shape=(n, n_renderings, 5))
            renderings = dst.create_dataset(
                'renderings', shape=(n, n_renderings), dtype=vlen_dtype)

            bar = IncrementalBar(max=n)
            for dst_index, example_id in enumerate(example_ids):
                src_index = indices[example_id]
                rle_data[dst_index] = src['rle_data'][src_index]
                meta[dst_index] = src['meta'][src_index]
                renderings[dst_index] = src['renderings'][src_index]
                bar.next()
            bar.finish()


for cat_id in get_cat_ids():
    fix(cat_id)
