import numpy as np
import os
import json
import zipfile
from path import annot_dir
from shapenet.image import load_image_from_zip
from io_util import parse_seg, parse_pts


def get_zip_path():
    return os.path.join(
        annot_dir, 'shapenetcore_partanno_segmentation_benchmark_v0.zip')


def get_zip_file():
    return zipfile.ZipFile(get_zip_path(), 'r')


def _subpath(topic, cat_id, example_id, ext):
    fn = '%s.%s' % (example_id, ext)
    return os.path.join(
        'shapenetcore_partanno_segmentation_benchmark_v0', cat_id, topic, fn)


def get_points(zip_file, cat_id, example_id):
    with zip_file.open(_subpath('points', cat_id, example_id, 'pts')) as fp:
        pts = parse_pts(fp)
    return np.array(pts, dtype=np.float32)


def get_point_labels(zip_file, cat_id, example_id):
    with zip_file.open(
            _subpath('points_label', cat_id, example_id, 'seg')) as fp:
        seg = parse_seg(fp)
    return np.array(seg, dtype=np.uint8)


def get_seg_image(zip_file, cat_id, example_id):
    with zip_file.open(
            _subpath('points_label', cat_id, example_id, 'png')) as fp:
        image = load_image_from_zip(fp)
    return image


def _read_ids(zip_file):
    ids = {}
    for name in zip_file.namelist():
        split = name.split('/')
        if len(split) < 4:
            continue
        _, cat_id, topic, fn = split
        if fn == '' or topic != 'points':
            continue
        example_id = fn.split('.')[0]
        if cat_id not in ids:
            ids[cat_id] = []
        ids[cat_id].append(example_id)
    ids = {k: sorted(v) for k, v in ids.items()}
    return ids


_ids_path = os.path.join(os.path.dirname(__file__), 'ids.json')


def get_ids():
    if not os.path.isfile(_ids_path):
        with get_zip_file() as zf:
            ids = _read_ids(zf)
            with open(_ids_path, 'w') as fp:
                json.dump(ids, fp)
    else:
        with open(_ids_path, 'r') as fp:
            ids = json.load(fp)
    return ids


if __name__ == '__main__':
    def vis(points, labels, image):
        from segment import segment
        from mayavi import mlab
        import matplotlib.pyplot as plt
        colors = (
            (1, 1, 1),
            (0, 1, 0),
            (0, 0, 1),
            (1, 0, 0),
            (0, 1, 1),
            (1, 1, 0),
            (1, 0, 1),
            (0, 0, 0)
        )
        points = segment(points, labels)
        for i, ps in enumerate(points):
            color = colors[i % len(colors)]
            x, z, y = ps.T
            mlab.points3d(x, y, z, color=color, scale_factor=0.005)
        if image is not None:
            plt.imshow(image)
            plt.show(block=False)
        mlab.show()

    ids = get_ids()
    cat_id = '02691156'
    example_ids = ids[cat_id]
    with get_zip_file() as zf:
        for example_id in example_ids:
            points = get_points(zf, cat_id, example_id)
            labels = get_point_labels(zf, cat_id, example_id)
            try:
                image = get_seg_image(zf, cat_id, example_id)
            except KeyError:
                image = None
            vis(points, labels, image)

    # from ffd.templates import get_templated_cat_ids
    # from ffd.templates import get_templated_example_ids
    # from shapenet.core import cat_id_to_desc
    # ids = get_ids()
    # counts = {}
    # for cat_id in get_templated_cat_ids():
    #     desc = cat_id_to_desc(cat_id)
    #     counts[cat_id] = 0
    #     if cat_id not in ids:
    #         print('No template data for CAT %s' % desc)
    #     else:
    #         cid = set(ids[cat_id])
    #         for example_id in get_templated_example_ids(cat_id):
    #             if example_id not in cid:
    #                 print('No template data for %s/%s' %(cat_id, example_id))
    #             else:
    #                 counts[cat_id] += 1
    #
    # for k, v in counts.items():
    #     print('%s: %d / %d' % (cat_id_to_desc(k), v, 30))
