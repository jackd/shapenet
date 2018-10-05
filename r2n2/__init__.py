from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


cat_descs = (
    'plane',
    'bench',
    'cabinet',
    'car',
    'chair',
    'monitor',
    'lamp',
    'speaker',
    'rifle',
    'sofa',
    'table',
    'telephone',
    'watercraft',
)


def get_cat_descs():
    return cat_descs


def get_cat_ids():
    from ..core import cat_desc_to_id
    return tuple(cat_desc_to_id(desc) for desc in cat_descs)


__all__ = [
    get_cat_ids,
    get_cat_descs,
    cat_descs,
]
