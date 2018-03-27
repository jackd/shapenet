import path
from path import get_cat_ids
from path import get_example_ids

_cat_descs = {
    '02691156': 'plane',
    # '02924116': 'bus',
    '02958343': 'car',
    '03001627': 'chair',
    '04256520': 'sofa',
    '04379243': 'table',
    # '02834778': 'bicycle',
    # '03790512': 'motorbike',
    '02933112': 'cabinet',
    '03211117': 'monitor',
    # '03211117': 'display',
    '03636649': 'lamp',
    '03691459': 'speaker',
    '04530566': 'watercraft',
    '03948459': 'pistol',
    '02992529': 'cellphone',
    '02828884': 'bench',
    '02818832': 'bed',
    '03207941': 'dishwasher',
}

_cat_ids = {v: k for k, v in _cat_descs.items()}


def cat_id_to_desc(cat_id):
    return _cat_descs[cat_id]


def cat_desc_to_id(cat_desc):
    return _cat_ids[cat_desc]


def to_cat_desc(cat):
    if cat in _cat_descs:
        return _cat_descs[cat]
    elif cat in _cat_ids:
        return cat
    else:
        raise ValueError('cat %s is not a valid id or descriptor' % cat)


def to_cat_id(cat):
    if cat in _cat_ids:
        return _cat_ids[cat]
    elif cat in _cat_descs:
        return cat
    else:
        raise ValueError('cat %s is not a valid id or descriptor' % cat)


__all__ = [
    path,
    get_cat_ids,
    get_example_ids,
    cat_id_to_desc,
    cat_desc_to_id,
]
