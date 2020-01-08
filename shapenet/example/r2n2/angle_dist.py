#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from shapenet.r2n2 import get_cat_ids
from shapenet.r2n2.hdf5 import Hdf5Manager, meta_index

az_index = meta_index('azimuth')
el_index = meta_index('elevation')
az = []
el = []

for cat_id in get_cat_ids():
    with Hdf5Manager(cat_id) as manager:
        g = manager.meta_group
        az.append(np.array(g[..., az_index]))
        el.append(np.array(g[..., el_index]))

az = np.concatenate(az, axis=0).flatten()
el = np.concatenate(el, axis=0).flatten()


def vis(az, el):
    import matplotlib.pyplot as plt
    _, (ax0, ax1) = plt.subplots(1, 2)
    ax0.hist(az, bins=36)
    ax1.hist(el, bins=36)
    plt.show()


vis(az, el)
