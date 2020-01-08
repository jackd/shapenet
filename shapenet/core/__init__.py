from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import six
from . import path

_cat_descs = {
  '02691156': 'plane',
  '02773838': 'bag',
  '02801938': 'basket',
  '02808440': 'bathtub',
  '02818832': 'bed',
  '02828884': 'bench',
  '02834778': 'bicycle',
  '02843684': 'birdhouse',
  '02871439': 'bookshelf',
  '02876657': 'bottle',
  '02880940': 'bowl',
  '02924116': 'bus',
  '02933112': 'cabinet',
  '02747177': 'can',
  '02942699': 'camera',
  '02954340': 'cap',
  '02958343': 'car',
  '03001627': 'chair',
  '03046257': 'clock',
  '03207941': 'dishwasher',
  '03211117': 'monitor',
  '04379243': 'table',
  '04401088': 'telephone',
  '02946921': 'tin_can',
  '04460130': 'tower',
  '04468005': 'train',
  '03085013': 'keyboard',
  '03261776': 'earphone',
  '03325088': 'faucet',
  '03337140': 'file',
  '03467517': 'guitar',
  '03513137': 'helmet',
  '03593526': 'jar',
  '03624134': 'knife',
  '03636649': 'lamp',
  '03642806': 'laptop',
  '03691459': 'speaker',
  '03710193': 'mailbox',
  '03759954': 'microphone',
  '03761084': 'microwave',
  '03790512': 'motorcycle',
  '03797390': 'mug',
  '03928116': 'piano',
  '03938244': 'pillow',
  '03948459': 'pistol',
  '03991062': 'pot',
  '04004475': 'printer',
  '04074963': 'remote_control',
  '04090263': 'rifle',
  '04099429': 'rocket',
  '04225987': 'skateboard',
  '04256520': 'sofa',
  '04330267': 'stove',
  '04530566': 'watercraft',
  '04554684': 'washer',
  '02858304': 'boat',
  '02992529': 'cellphone'
}


def get_cat_ids():
    cat_ids = list(_cat_descs.keys())
    cat_ids.sort()
    return tuple(cat_ids)


_cat_ids = {v: k for k, v in _cat_descs.items()}


def get_test_train_split():
    import os
    split_path = path.get_test_train_split_path()
    if not os.path.isfile(split_path):
        import wget
        url = ('http://shapenet.cs.stanford.edu/shapenet/obj-zip/SHREC16/'
               'all.csv')
        wget.download(url, split_path)
        if not os.path.isfile(split_path):
            raise IOError('Failed to download test/train split from %s' % url)

    split = {k: {'train': [], 'test': [], 'val': []} for k in get_cat_ids()}
    with open(split_path, 'r') as fp:
        fp.readline()
        for line in fp.readlines():
            line = line.rstrip()
            if len(line) > 0:
                _, cat_id, __, example_id, ds = line.split(',')
                split[cat_id][ds].append(example_id)
    return split


def cat_id_to_desc(cat_id):
    if isinstance(cat_id, (list, tuple)):
        return tuple(_cat_descs[c] for c in cat_id)
    else:
        return _cat_descs[cat_id]


def cat_desc_to_id(cat_desc):
    if isinstance(cat_desc, (list, tuple)):
        return tuple(_cat_ids[c] for c in cat_desc)
    else:
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


def get_example_ids(cat_id, include_bad=False):
    from .path import get_ids_path
    ids_path = get_ids_path(cat_id)
    if not os.path.isfile(ids_path):
        create_ids(cat_id)
    with open(ids_path, 'r') as fp:
        ids = fp.readlines()
    ids = [id.rstrip() for id in ids]
    ids.sort()
    if not include_bad:
        from .objs import get_bad_objs
        bad_objs = get_bad_objs(cat_id)
        ids = (i for i in ids if i not in bad_objs)
    return tuple(ids)


def get_old_example_ids(cat_id):
    from .path import get_ids_path
    with open(get_ids_path(cat_id), 'r') as fp:
        ids = fp.readlines()
    ids = [id.rstrip() for id in ids]
    return ids


def create_ids(cat_ids):
    from progress.bar import IncrementalBar
    if isinstance(cat_ids, six.string_types):
        cat_ids = [cat_ids]
    bar = IncrementalBar(max=len(cat_ids))
    for cat_id in cat_ids:
        ids_path = path.get_ids_path(cat_id)
        d = os.path.dirname(ids_path)
        if not os.path.isdir(d):
            os.makedirs(d)
        example_ids = path.get_example_ids_from_zip(cat_id)
        with open(ids_path, 'w') as fp:
            fp.writelines(
                ('%s\n' % example_id for example_id in example_ids))
        bar.next()
    bar.finish()


# __all__ = [
#     path,
#     get_cat_ids,
#     get_example_ids,
#     cat_id_to_desc,
#     cat_desc_to_id,
# ]
