#!/usr/bin/python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from shapenet.r2n2.renderings import RenderingsManager
from shapenet.r2n2.binvox import BinvoxManager


print('Opening BM')
with BinvoxManager() as bm:
    print('Getting exmaple_ids...')
    example_ids = bm.get_example_ids()

print('Opening RM')
with RenderingsManager() as rm:
    print('Getting metas...')
    for cat_id, example_ids in example_ids.items():
        for example_id in example_ids:
            metas = rm.get_metas(cat_id, example_id)
            print(cat_id, example_id, len(metas))
