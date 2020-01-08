from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def get_start_end_frac(mode):
    if mode == 'train':
        start_frac = 0
        end_frac = 0.8
    elif mode == 'test':
        start_frac = 0.8
        end_frac = 1
    else:
        raise ValueError(
            '`mode` must be one of ("train", "test"), got "%s" % mode')
    return start_frac, end_frac


def get_start_end_index(n_examples, mode):
    start, end = get_start_end_frac(mode)
    return int(n_examples*start), int(n_examples*end)


def _split(sorted_keys, mode):
    start, end = get_start_end_index(len(sorted_keys), mode)
    return sorted_keys[start:end]


def split(example_ids, mode):
    example_ids = sorted(example_ids)
    return _split(example_ids, mode)


def split_indices(example_ids, mode):
    enumerated = sorted(enumerate(example_ids), key=lambda x: x[1])
    indices, keys = zip(*_split(enumerated, mode))
    return indices
