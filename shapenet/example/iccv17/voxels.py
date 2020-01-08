#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from util3d.mayavi_vis import vis_voxels, vis_point_cloud
from mayavi import mlab
from util3d.voxel.manip import fast_resize, get_surface_voxels
from util3d.voxel.convert import voxels_to_point_cloud

from shapenet.iccv17.voxels import get_mat_data

voxels = get_mat_data('eval', 9)


def test_fast_resize():
    # zoomed = resize(voxels, 64)
    vis_voxels(fast_resize(voxels, 32), color=(0, 0, 1), axis_order='xyz')
    mlab.show()


def test_surface_voxels():
    point_cloud = voxels_to_point_cloud(get_surface_voxels(voxels))
    vis_point_cloud(point_cloud[:len(point_cloud) // 2], color=(0, 0, 1))
    mlab.show()


def test_mpl_vis():
    print(voxels.shape)
    v = fast_resize(voxels, 32)
    print(v.shape)
    vis_voxels(v, color=(0, 0, 1), axis_order='xyz')
    mlab.show()


test_mpl_vis()
test_fast_resize()
test_surface_voxels()
