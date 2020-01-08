from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class ViewManager(object):
    @property
    def view_id(self):
        return self.get_view_params()['view_id']

    def get_view_params(self):
        raise NotImplementedError('Abstract method')

    def get_camera_positions(self, cat_id, example_id):
        raise NotImplementedError('Abstract method')

    def get_example_ids(self, cat_id):
        raise NotImplementedError('Abstract method')

    def get_cat_ids(self):
        raise NotImplementedError('Abstract method')

    def keys(self, cat_ids=None):
        if cat_ids is None:
            cat_ids = self.get_cat_ids()
        for cat_id in cat_ids:
            for example_id in self.get_example_ids(cat_id):
                yield (cat_id, example_id)

    def to_dict(self):
        raise NotImplementedError('Abstract method')


class WritableViewManager(ViewManager):
    def set_view_params(self, **params):
        raise NotImplementedError('Abstract method')

    def set_camera_positions(self, cat_id, example_id, positions):
        raise NotImplementedError('Abstract method')

    def copy_from(self, src_manager):
        self.set_view_params(**src_manager.get_view_params())

        for cat_id in src_manager.get_cat_ids():
            for example_id in src_manager.get_example_ids(cat_id):
                positions = src_manager.get_camera_positions(
                    cat_id, example_id)
                self.set_camera_positions(cat_id, example_id, positions)
