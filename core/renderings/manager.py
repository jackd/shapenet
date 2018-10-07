from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import numpy as np
from ..fixed_objs import is_bad_obj, get_fixed_obj_path

_root_dir = os.path.realpath(os.path.dirname(__file__))
renderings_dir = os.path.join(_root_dir, '_renderings')


def get_default_manager_dir(manager_id):
    return os.path.join(renderings_dir, manager_id)


def has_renderings(folder, n_renderings, files_per_rendering=4):
    return os.path.isdir(folder) and \
            len(os.listdir(folder)) == files_per_rendering*n_renderings


class RenderingsManager(object):
    def get_image(self, key, view_index, suffix=None):
        raise NotImplementedError('Abstract method')

    def get_camera_positions(self, key):
        raise NotImplementedError('Abstract method')

    def keys(self):
        raise NotImplementedError('Abstract method')


class RenderableManager(RenderingsManager):
    def get_obj_path(self, key):
        raise NotImplementedError('Abstract method')

    def get_rendering_path(self, key, view_index, suffix=None):
        raise NotImplementedError('Abstract method')

    def get_render_params(self):
        raise NotImplementedError('Abstract method')

    def needs_rendering_keys():
        raise NotImplementedError('Abstract method')

    def get_image(self, key, view_index, suffix=None):
        from PIL import Image
        return Image.open(self.get_rendering_path(key, view_index, suffix))


def _get_render_params(**kwargs):
    default_params = dict(
        depth_scale=1.4,
        scale=1,
        shape=[128, 128],
        edge_split=False,
        remove_doubles=False,
        n_renderings=24,
    )
    for k, v in kwargs.items():
        if k in default_params:
            default_params[k] = v
        else:
            raise KeyError('Invalid key "%s"' % k)
    default_params['shape'] = tuple(default_params['shape'])
    return default_params


class RenderableManagerBase(RenderableManager):
    def __init__(self, root_dir, cat_ids=None):
        self._root_dir = root_dir
        self._render_params = None
        if cat_ids is None:
            from shapenet.r2n2 import get_cat_ids
            self._cat_ids = get_cat_ids()
        self._cat_ids = tuple(cat_ids)

    def keys(self):
        from shapenet.core import get_example_ids
        for cat_id in self._cat_ids:
            for example_id in get_example_ids(cat_id):
                yield (cat_id, example_id)

    def needs_rendering_keys(self):
        n_renderings = self._p['n_renderings']
        files_per_rendering = 4
        return (k for k in self.keys() if not has_renderings(
            self.get_rendering_dir(k), n_renderings, files_per_rendering))

    @property
    def root_dir(self):
        return self._root_dir

    def _path(self, *subpaths):
        return os.path.join(self.root_dir, *subpaths)

    @property
    def _render_path(self):
        return self._path('render_params.json')

    def check_render_params(self, **render_params):
        if self._get_render_params() != _get_render_params(**render_params):
            raise IOError(
                'render_params provided inconsistent with those saved '
                'to file.')

    def set_render_params(self, **render_params):
        render_params = _get_render_params(**render_params)
        root_dir = self.root_dir
        if not os.path.isdir(root_dir):
            os.makedirs(root_dir)

        path = self._render_path
        if os.path.isfile(path):
            self.check_render_params(**render_params)
        else:
            with open(path, 'w') as fp:
                json.dump(render_params, fp)

    def _get_render_params(self):
        if self._render_params is None:
            path = self._render_path
            if not os.path.isfile(path):
                raise IOError('No params at %s' % path)
            with open(path, 'r') as fp:
                params = json.load(fp)
                self._render_params = {
                    k: tuple(v) if isinstance(v, list) else v
                    for k, v in params.items()}
        return self._render_params

    @property
    def _p(self):
        return self._get_render_params()

    def get_render_params(self):
        return self._p.copy()

    def _get_camera_positions_path(self, key):
        cat_id, example_id = key
        return self._path('camera_positions', cat_id, '%s.txt' % example_id)

    def get_camera_positions(self, key):
        path = self._get_camera_positions_path(key)
        if os.path.isfile(path):
            with open(path, 'r') as fp:
                out = [
                    [float(x) for x in line.rstrip().split(' ')]
                    for line in fp.readlines()]
        else:
            raise IOError('No camera positions at %s' % path)
        return out

    def set_camera_positions(self, key, camera_positions):
        path = self._get_camera_positions_path(key)
        if os.path.isfile(path):
            raise ValueError(
                'Cannot set camera positions: file already exists at %s'
                % path)
        camera_positions = np.array(camera_positions, copy=False)
        if camera_positions.shape[1:] != (3,):
            raise ValueError('camera_positions must be (N, 3)')
        dir = os.path.dirname(path)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        np.savetxt(path, camera_positions)

    def get_obj_path(self, key):
        from shapenet.core.path import get_extracted_core_dir
        cat_id, example_id = key
        if is_bad_obj(cat_id, example_id):
            return get_fixed_obj_path(cat_id, example_id)
        else:
            return os.path.join(
                get_extracted_core_dir(), cat_id, example_id, 'model.obj')

    def get_rendering_dir(self, key):
        cat_id, example_id = key
        return self._path('renderings', cat_id, example_id)

    def get_rendering_path(self, key, view_index, suffix=None):
        fn = ('r%03d.png' % view_index) if suffix is None else \
            'r%03d_%s.png' % (view_index, suffix)
        return os.path.join(self.get_rendering_dir(key), fn)

    def render_all(
            self, verbose=True, blender_path='blender'):
        import subprocess
        _FNULL = open(os.devnull, 'w')
        call_kwargs = dict()
        if not verbose:
            call_kwargs['stdout'] = _FNULL
            call_kwargs['stderr'] = subprocess.STDOUT

        script_path = os.path.join(_root_dir, 'scripts', 'blender_render.py')
        print(
            'Rendering %d examples. This could take some time...'
            % len(tuple(self.needs_rendering_keys())))
        args = [
            blender_path, '--background',
            '--python', script_path, '--',
            '--manager_dir', self.root_dir,
            '--cat_id'] + list(self._cat_ids)
        proc = subprocess.Popen(args, **call_kwargs)
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            raise


def get_base_manager(dim=128, turntable=False, n_renderings=24, cat_ids=None):
    manager_id = '%s-%03d-%03d' % (
        'turntable' if turntable else 'rand', dim, n_renderings)
    manager = RenderableManagerBase(
        get_default_manager_dir(manager_id), cat_ids=cat_ids)
    manager.set_render_params(n_renderings=n_renderings, shape=(dim,)*2)
    return manager


def create_base_manager(dim=128, turntable=False, n_renderings=24):
    from progress.bar import IncrementalBar
    from shapenet.r2n2 import get_cat_ids
    manager = get_base_manager(
        dim=dim, turntable=turntable, n_renderings=n_renderings,
        cat_ids=get_cat_ids())
    dist = 1.166  # sqrt(1 + 0.6**2) - looked good in experiments

    def polar_to_cartesian(dist, theta, phi):
        z = np.cos(phi)
        s = np.sin(phi)
        x = s * np.cos(theta)
        y = s * np.sin(theta)
        return np.stack((x, y, z), axis=-1) * dist

    if turntable:
        def get_camera_pos():
            theta = np.deg2rad(np.linspace(0, 360, n_renderings+1)[:-1])
            phi = np.deg2rad(60.0) * np.ones_like(theta)
            return polar_to_cartesian(dist, theta, phi).astype(np.float32)
    else:
        def get_camera_pos():
            size = (n_renderings,)
            theta = np.deg2rad(np.random.uniform(0, 360, size=size))
            phi = np.deg2rad(90 - np.random.uniform(25, 30, size=size))
            return polar_to_cartesian(dist, theta, phi).astype(np.float32)

    keys = manager.keys()
    print('Creating random r2n2 renderings manager')
    bar = IncrementalBar(max=len(keys))

    for key in keys:
        manager.set_camera_positions(key, get_camera_pos())
        bar.next()
    bar.finish()
