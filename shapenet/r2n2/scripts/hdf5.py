#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import shapenet.r2n2.tgz as tgz
import shapenet.r2n2.hdf5 as hdf5

overwrite = False
# overwrite = True

with tgz.BinvoxManager() as bm:
    example_ids = bm.get_example_ids()


n = len(example_ids)
for i, (cat_id, ex_ids) in enumerate(example_ids.items()):
    print('Converting %s, %d / %d' % (cat_id, i+1, n))
    with hdf5.Converter(cat_id, ex_ids, mode='a') as converter:
        converter.convert(overwrite=overwrite)
