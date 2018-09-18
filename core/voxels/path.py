import os
from shapenet.path import shapenet_dir

data_dir = os.path.join(shapenet_dir, 'core', 'voxels', '_data')
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)


def get_voxel_id(voxel_dim=32, exact=True, dc=True, aw=True):
    def bstr(b):
        return 't' if b else 'f'
    return 'd%03d%s%s%s' % (voxel_dim, bstr(exact), bstr(dc), bstr(aw))


default_voxel_id = get_voxel_id()


def parse_voxel_id(voxel_id):
    """Inverse function to `get_voxel_id`."""
    if not is_valid_voxel_id(voxel_id):
        raise ValueError('voxel_id %s not valid.' % voxel_id)
    return dict(
        voxel_dim=int(voxel_id[1:4]),
        exact=voxel_id[4] == 't',
        dc=voxel_id[5] == 't',
        aw=voxel_id[6] == 't',
    )


def is_valid_voxel_id(voxel_id):
    if not isinstance(voxel_id, (str, unicode)) or len(voxel_id) != 7:
        return False
    try:
        int3 = int(voxel_id[1:4])
    except ValueError:
        return False
    if int3 <= 0:
        return False
    return voxel_id[0] == 'd' and all(s in ('t', 'f') for s in voxel_id[4:])


def get_binvox_subpath(cat_id, example_id=None):
    if example_id is None:
        return cat_id
    return os.path.join(cat_id, '%s.binvox' % example_id)


def get_binvox_dir(voxel_id):
    return os.path.join(data_dir, voxel_id)


def get_rotated_binvox_dir(voxel_id):
    return os.path.join(data_dir, 'rotated', voxel_id)


# def has_binvox_data(voxel_id, cat_id, example_id=None):
#     return os.path.exists(get_binvox_path(voxel_id, cat_id, example_id))
