import os
import json
import numpy as np
from io_util import parse_seg
from path import _get_subpath

_seg_names_path = os.path.join(os.path.dirname(__file__), 'seg_names.json')


def _get_cat_dir(cat_id):
    return os.path.join('PartAnnotation', cat_id, 'points_label')


def get_segmentation_names(cat_id=None):
    if not os.path.isfile(_seg_names_path):
        names = _create_segmentation_names()
        with open(_seg_names_path, 'w') as fp:
            json.dump(names, fp)
    else:
        with open(_seg_names_path, 'r') as fp:
            names = json.load(fp)

    if cat_id is None:
        return names
    else:
        return names[cat_id]


def get_binary_point_labels(zipfile, cat_id, example_id, seg_name):
    path = _get_subpath(
        cat_id, example_id, os.path.join('points_label', seg_name), 'seg')
    with zipfile.open(path) as fp:
        labels = parse_seg(fp)
    return labels


def get_point_labels(zipfile, cat_id, example_id):
    names = get_segmentation_names(cat_id)
    result = get_binary_point_labels(zipfile, cat_id, example_id, names[0])
    result = np.array(result, dtype=np.uint8)
    for i, name in enumerate(names[1:]):
        bin_seg = get_binary_point_labels(zipfile, cat_id, example_id, name)
        result[bin_seg] = i + 2
    return result


def _create_segmentation_names():
    from path import get_zip_file
    names = {}
    with get_zip_file() as zf:
        for n in zf.namelist():
            split = n.split('/')
            if len(split) >= 4 and split[2] == 'points_label':
                cat_id = split[1]
                class_name = split[3]
                if cat_id not in names:
                    names[cat_id] = set()
                names[cat_id].add(class_name)

    def map_fn(s):
        li = list(s)
        li.sort()
        li = [v for v in li if v != '']
        return li

    return {k: map_fn(v) for k, v in names.items()}


def _main():
    from path import get_zip_file
    from points import get_points
    # from expert_verified import get_seg_image
    from shapenet.core.meshes import get_mesh_dataset
    # import matplotlib.pyplot as plt
    from mayavi import mlab
    cat_id = '02691156'
    # example_id = '1a04e3eab45ca15dd86060f189eb133'
    # example_id = '1a6ad7a24bb89733f412783097373bdc'
    example_id = '1a9b552befd6306cc8f2d5fe7449af61'
    with get_zip_file() as f:
        points = get_points(f, cat_id, example_id)
        labels = get_point_labels(f, cat_id, example_id)
        names = get_segmentation_names(cat_id)
        # image = get_seg_image(f, cat_id, example_id)
    print(len(points))
    names = ['unlabelled'] + names

    clouds = []
    for i, name in enumerate(names):
        cloud = points[labels == i]
        clouds.append(cloud)
        print('%s: %d' % (name, len(cloud)))

    with get_mesh_dataset(cat_id) as mesh_ds:
        example = mesh_ds[example_id]
        vertices, faces = (np.array(example[k]) for k in ('vertices', 'faces'))

    x, z, y = vertices.T
    mlab.triangular_mesh(x, y, z, faces, color=(1, 1, 1))
    mlab.triangular_mesh(
        x, y, z, faces, color=(0, 0, 0), representation='wireframe')

    colors = np.random.uniform(size=(np.max(labels)+1, 3))
    for color, cloud in zip(colors, clouds):
        x, z, y = cloud.T
        mlab.points3d(
            x, y, z, color=tuple(color), opacity=0.8, scale_factor=0.02)
    print(np.min(points, axis=0), np.max(points, axis=0))
    print(np.min(vertices, axis=0), np.max(vertices, axis=0))
    # plt.imshow(image)
    # plt.show(block=False)
    mlab.show()
    # plt.close()


if __name__ == '__main__':
    _main()
