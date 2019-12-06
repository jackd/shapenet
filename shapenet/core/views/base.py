from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def get_base_id(turntable=False, n_views=24):
    return '%s-%03d' % (
        'turntable' if turntable else 'rand', n_views)


def get_base_manager(turntable=False, n_views=24, format='h5'):
    if format == 'zip':
        from .archive import get_base_zip_manager
        fn = get_base_zip_manager
    elif format == 'txt':
        from .txt import get_base_txt_manager
        fn = get_base_txt_manager
    elif format == 'h5':
        from .h5 import get_base_h5_manager
        fn = get_base_h5_manager
    elif format == 'lazy':
        from .lazy import get_base_lazy_manager
        fn = get_base_lazy_manager
    else:
        raise ValueError('Unrecognized format "%s"' % format)
    return fn(turntable=turntable, n_views=n_views)
