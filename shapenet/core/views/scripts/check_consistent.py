#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from shapenet.core.views.txt import get_base_txt_manager
from shapenet.core.views.h5 import get_base_h5_manager
from shapenet.core.views.archive import get_base_zip_manager

txt = get_base_txt_manager()
h5 = get_base_h5_manager()
zi = get_base_zip_manager()

cat_id = h5.get_cat_ids()[2]
example_id = h5.get_example_ids(cat_id)[10]

hc = h5.get_camera_positions(cat_id, example_id)
tc = txt.get_camera_positions(cat_id, example_id)
zc = zi.get_camera_positions(cat_id, example_id)

print(hc)
print(tc)
print(zc)
print(hc - tc)
print(hc - zc)

print('Checking params...')
hp = h5.get_view_params()
tp = txt.get_view_params()
zp = zi.get_view_params()

for k, v in hp.items():
    assert(tp[k] == v)
    assert(zp[k] == v)

assert(len(hp) == len(tp))
assert(len(hp) == len(zp))
print('Consistent!')
