from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import yaml
import json
import os
import numpy as np
from ..fixed_objs import is_fixed_obj, get_fixed_obj_path
from .path import get_renderings_subdir


def _get_core_renderings_dir():
    from ..path import get_data_dir
    return get_data_dir('renderings')


renderings_dir = _get_core_renderings_dir()


def get_default_manager_dir(manager_id):
    return os.path.join(renderings_dir, manager_id)


def has_renderings(folder, n_renderings, files_per_rendering=4):
    return os.path.isdir(folder) and \
            len(os.listdir(folder)) == files_per_rendering*n_renderings


class RenderingsManager(object):
    @property
    def view_manager(self):
        raise NotImplementedError('Abstract property')

    def get_image(self, cat_id, example_id, view_index):
        raise NotImplementedError('Abstract method')


class RenderableManager(RenderingsManager):
    def get_obj_path(self, cat_id, example_id):
        raise NotImplementedError('Abstract method')

    def get_rendering_path(self, cat_id, example_id, view_index):
        raise NotImplementedError('Abstract method')

    def get_view_params(self):
        raise NotImplementedError('Abstract method')

    def get_image_params(self):
        raise NotImplementedError('Abstract method')

    def needs_rendering_keys(self):
        raise NotImplementedError('Abstract method')

    def get_image(self, cat_id, example_id, view_index):
        from PIL import Image
        return Image.open(
            self.get_rendering_path(cat_id, example_id, view_index))


class RenderableManagerBase(RenderableManager):
    def __init__(self, root_dir, view_manager, image_shape):
        self._root_dir = root_dir
        self._view_manager = view_manager
        self._view_params = view_manager.get_view_params()
        self._image_shape = image_shape
        self._renderings_dir = os.path.join(root_dir, 'renderings')

    @property
    def view_manager(self):
        return self._view_manager

    def get_view_params(self):
        return self._view_params.copy()

    def needs_rendering_keys(self, cat_ids=None):
        n_views = self.get_view_params()['n_views']
        files_per_rendering = 4
        return (
            k for k in self.view_manager.keys(cat_ids)
            if not has_renderings(
                self.get_renderings_dir(*k), n_views, files_per_rendering))

    @property
    def root_dir(self):
        return self._root_dir

    def _path(self, *subpaths):
        return os.path.join(self.root_dir, *subpaths)

    @property
    def _image_params_path(self):
        return self._path('image_params.yaml')

    def get_image_params(self):
        path = self._image_params_path
        if not os.path.isfile(path):
            raise IOError('No image_params saved at %s' % path)
        with open(path, 'r') as fp:
            return yaml.load(fp)

    def set_image_params(self, **image_params):
        path = self._image_params_path
        folder = os.path.dirname(path)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        if os.path.isfile(path):
            self.check_image_params(**image_params)
        else:
            with open(path, 'w') as fp:
                yaml.dump(image_params, fp, default_flow_style=False)

    def check_image_params(self, **image_params):
        saved = self.get_image_params()
        if saved != image_params:
            raise ValueError(
                'image_params not consistent with saved image_params\n'
                'saved_image_params:\n'
                '%s\n'
                'passed image_params:\n'
                '%s\n' % (saved, image_params))

    def get_obj_path(self, cat_id, example_id):
        from shapenet.core.path import get_extracted_core_dir
        if is_fixed_obj(cat_id, example_id):
            return get_fixed_obj_path(cat_id, example_id)
        else:
            return os.path.join(
                get_extracted_core_dir(), cat_id, example_id, 'model.obj')

    def get_renderings_dir(self, cat_id, example_id):
        return os.path.join(
            self._renderings_dir, get_renderings_subdir(cat_id, example_id))

    def get_rendering_path(self, cat_id, example_id, view_index):
        from . import path
        subpath = path.get_rendering_subpath(cat_id, example_id, view_index)
        return os.path.join(self._renderings_dir, subpath)

    def get_cat_dir(self, cat_id):
        return os.path.join(
            self._renderings_dir, get_renderings_subdir(cat_id))

    def render_all(
            self, cat_ids=None, verbose=True, blender_path='blender'):
        import subprocess
        from progress.bar import IncrementalBar
        import tempfile
        from .path import renderings_format
        from ..objs import try_extract_models
        for cat_id in cat_ids:
            try_extract_models(cat_id)
        _FNULL = open(os.devnull, 'w')
        call_kwargs = dict()
        if not verbose:
            call_kwargs['stdout'] = _FNULL
            call_kwargs['stderr'] = subprocess.STDOUT

        root_dir = os.path.realpath(os.path.dirname(__file__))
        script_path = os.path.join(root_dir, 'scripts', 'blender_render.py')

        render_params_path = None
        camera_positions_path = None

        def clean_up():
            for path in (render_params_path, camera_positions_path):
                if path is not None and os.path.isfile(path):
                    os.remove(path)

        render_params_fp, render_params_path = tempfile.mkstemp(suffix='.json')
        try:
            view_params = self.get_view_params()
            view_params.update(**self.get_image_params())
            os.write(render_params_fp, json.dumps(view_params))
            os.close(render_params_fp)

            args = [
                blender_path, '--background',
                '--python', script_path, '--',
                '--render_params', render_params_path]

            keys = tuple(self.needs_rendering_keys(cat_ids))
            n = len(keys)
            if n == 0:
                print('No keys to render.')
                return
            print('Rendering %d examples' % n)
            bar = IncrementalBar(max=n)
            for cat_id, example_id in keys:
                bar.next()

                camera_positions_fp, camera_positions_path = tempfile.mkstemp(
                    suffix='.npy')
                os.close(camera_positions_fp)
                np.save(
                    camera_positions_path,
                    self.view_manager.get_camera_positions(cat_id, example_id))

                out_dir = self.get_renderings_dir(cat_id, example_id)
                proc = subprocess.Popen(
                    args + [
                        '--obj', self.get_obj_path(cat_id, example_id),
                        '--out_dir', out_dir,
                        '--filename_format', renderings_format,
                        '--camera_positions', camera_positions_path,
                        ],
                    **call_kwargs)
                try:
                    proc.wait()
                except KeyboardInterrupt:
                    proc.kill()
                    raise
                if os.path.isfile(camera_positions_path):
                    os.remove(camera_positions_path)
            bar.finish()
        except (Exception, KeyboardInterrupt):
            clean_up()
            raise
        clean_up()


def get_base_manager(turntable=False, n_views=24, format='h5', dim=128):
    from ..views.base import get_base_manager, get_base_id
    kwargs = dict(turntable=turntable, n_views=n_views)
    manager_id = '%s-%03d' % (get_base_id(**kwargs), dim)
    manager = RenderableManagerBase(
        get_default_manager_dir(manager_id), get_base_manager(**kwargs),
        (dim,)*2)
    manager.set_image_params(shape=(dim,)*2)
    return manager
