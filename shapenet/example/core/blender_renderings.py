#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import matplotlib.pyplot as plt
from shapenet.image import with_background
from shapenet.core.blender_renderings.config import RenderConfig
from shapenet.core import cat_desc_to_id, get_example_ids


cat_desc = 'plane'
view_index = 5
config = RenderConfig()
view_angle = config.view_angle(view_index)
cat_id = cat_desc_to_id(cat_desc)
example_ids = get_example_ids(cat_id)

path = config.get_zip_path(cat_id)
if not os.path.isfile(path):
    raise IOError('No renderings at %s' % path)

with config.get_dataset(cat_id, view_index) as ds:
    ds = ds.map(lambda image: with_background(image, 255))
    for example_id in ds:
        image = ds[example_id]
        plt.imshow(image)
        plt.show()
