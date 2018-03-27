import os

blender_renderings_dir = os.path.realpath(os.path.dirname(__file__))
images_dir = os.path.join(blender_renderings_dir, '_images')


def get_renderings_dir(config_id):
    return os.path.join(images_dir, config_id)


def get_cat_dir(config_id, cat_id):
    return os.path.join(get_renderings_dir(config_id), cat_id)


def get_example_dir(config_id, cat_id, example_id):
    return os.path.join(get_cat_dir(config_id, cat_id), example_id)


def _get_example_subpath(cat_id, example_id, view_angle, extra):
    return os.path.join(
        cat_id, example_id,
        '%s_r_%03d%s.png' % (example_id, view_angle, extra))


def _get_example_path(config_id, cat_id, example_id, view_angle, extra):
    return os.path.join(
        get_renderings_dir(config_id),
        _get_example_subpath(cat_id, example_id, view_angle, extra))


def get_example_image_subpath(cat_id, example_id, view_angle):
    return _get_example_subpath(cat_id, example_id, view_angle, '')


def get_example_normals_subpath(cat_id, example_id, view_angle):
    return _get_example_subpath(
        cat_id, example_id, view_angle, '_normals.png0001')


def get_example_albedo_subpath(cat_id, example_id, view_angle):
    return _get_example_subpath(
        cat_id, example_id, view_angle, '_albedo.png0001')


def get_example_depth_subpath(cat_id, example_id, view_angle):
    return _get_example_subpath(
        cat_id, example_id, view_angle, '_depth.png0001')


def get_fixed_meshes_dir():
    return os.path.join(blender_renderings_dir, '_fixed_meshes')


def get_fixed_meshes_zip_path(cat_id):
    return os.path.join(get_fixed_meshes_dir(), '%s.zip' % cat_id)


if __name__ == '__main__':
    from shapenet.core import cat_desc_to_id, get_example_ids
    from shapenet.image import load_image_from_zip, with_background
    import random
    import zipfile
    import matplotlib.pyplot as plt
    from config import RenderConfig
    cat_desc = 'plane'
    cat_id = cat_desc_to_id(cat_desc)
    example_ids = get_example_ids(cat_id)
    random.shuffle(example_ids)

    config = RenderConfig()
    with zipfile.ZipFile(config.get_zip_path(cat_id), 'r') as zf:
        for example_id in example_ids:
            subpath = get_example_image_subpath(
                cat_id, example_id, config.view_angle(5))
            image = load_image_from_zip(zf, subpath)
            image = with_background(image, 255)
            plt.imshow(image)
            plt.show()
