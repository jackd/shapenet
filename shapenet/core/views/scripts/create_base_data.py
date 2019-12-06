#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def create_h5_data(**kwargs):
    from shapenet.core.views.h5 import get_base_h5_manager
    get_base_h5_manager(**kwargs)


def create_txt_data(**kwargs):
    from shapenet.core.views.txt import get_base_txt_manager
    get_base_txt_manager(**kwargs)


def create_zip_data(**kwargs):
    from shapenet.core.views.archive import get_base_zip_manager
    get_base_zip_manager(**kwargs)


# create_txt_data()
create_h5_data()
# create_zip_data()
