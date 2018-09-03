#!/usr/bin/python
"""Create uncompressed renderings."""
import os
import shutil
import subprocess
from datetime import datetime
from shapenet.path import get_temp_dir
from shapenet.core import get_example_ids, cat_desc_to_id
from shapenet.core.path import get_zip_path, get_example_subdir, \
    get_obj_subpath
from shapenet.core.blender_renderings.path import get_fixed_meshes_zip_path
from shapenet.core.blender_renderings.config import RenderConfig

_FNULL = open(os.devnull, 'w')


def render_obj(
        config, obj_path, output_dir, call_kwargs, blender_path='blender'):
    script_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), 'blender_render.py')
    scale_str = '1' if config.scale is None else str(config.scale)
    subprocess.call([
        blender_path,
        '--background',
        '--python', script_path, '--',
        '--views', str(config.n_images),
        '--shape', str(config.shape[0]), str(config.shape[1]),
        '--scale', scale_str,
        '--output_folder', output_dir,
        '--remove_doubles',
        '--edge_split',
        obj_path,
        ], **call_kwargs)


def get_file_index(zf):
    ret = {}
    for f in zf.namelist():
        key = f.split('/')
        if len(key) > 2:
            ret.setdefault('/'.join(key[:2]), []).append(f)
    return ret


def render_example(
        config, cat_id, example_id, zip_file, overwrite, call_kwargs,
        blender_path='blender', verbose=False, file_index=None):
    if file_index is None:
        print('Warning: computing file_index in render_example. '
              'Highly inefficient if rendering multiple examples')
        file_index = get_file_index(zip_file)
    subdir = get_example_subdir(cat_id, example_id)
    cat_dir = config.get_cat_dir(cat_id)
    example_dir = config.get_example_dir(cat_id, example_id)
    if not overwrite:
        if os.path.isdir(example_dir) and \
                len(os.listdir(example_dir)) == 4*config.n_images:
            return False
    else:
        if os.path.isdir(example_dir):
            shutil.rmtree(example_dir)
    if not os.path.isdir(cat_dir):
        os.makedirs(cat_dir)

    paths = file_index.get(subdir)
    if paths is None:
        return False

    with get_temp_dir() as tmp:
        for f in paths:
            zip_file.extract(f, tmp)
        # for f in zip_file.namelist():
        #     if f.startswith(subdir):
        #         zip_file.extract(f, tmp)
        subpath = get_obj_subpath(cat_id, example_id)
        obj_path = os.path.join(tmp, subpath)
        if verbose:
            print('')
            print(datetime.now())
            print('Rendering %s' % example_id)
        render_obj(
            config, obj_path, cat_dir, call_kwargs, blender_path=blender_path)
        return True


def render_cat(
        config, cat_id, overwrite, reverse=False, debug=False,
        example_ids=None, use_fixed_meshes=False, blender_path='blender',
        verbose=False):
    import zipfile
    from progress.bar import IncrementalBar
    call_kwargs = {} if debug else dict(
        stdout=_FNULL, stderr=subprocess.STDOUT)
    if example_ids is None or len(example_ids) == 0:
        example_ids = get_example_ids(cat_id)
    if reverse:
        example_ids = example_ids[-1::-1]
    print('Rendering %d images for cat %s' % (len(example_ids), cat_id))
    bar = IncrementalBar(max=len(example_ids))
    if use_fixed_meshes:
        zip_path = get_fixed_meshes_zip_path(cat_id)
    else:
        zip_path = get_zip_path(cat_id)
    with zipfile.ZipFile(zip_path) as zip_file:
        file_index = get_file_index(zip_file)
        for example_id in example_ids:
            bar.next()
            render_example(
                config, cat_id, example_id, zip_file,
                overwrite, call_kwargs, blender_path=blender_path,
                verbose=verbose, file_index=file_index)
    bar.finish()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str)
    parser.add_argument('--shape', type=int, nargs=2, default=[192, 256])
    parser.add_argument('--scale', type=float, default=None)
    parser.add_argument('--blender_path', type=str, default='blender')
    parser.add_argument('-n', '--n_images', type=int, default=8)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-r', '--reverse', action='store_true')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-i', '--example_ids', nargs='*')
    parser.add_argument('-f', '--fixed_meshes', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    config = RenderConfig(args.shape, args.n_images, args.scale)
    cat_id = cat_id = cat_desc_to_id(args.cat)
    render_cat(config, cat_id, args.overwrite, args.reverse, args.debug,
               args.example_ids, args.fixed_meshes, args.blender_path,
               args.verbose)
