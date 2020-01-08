import numpy as np
from path import _get_subpath
from io_util import parse_pts


def get_points(zipfile, cat_id, example_id, dtype=np.float32):
    subpath = _get_subpath(cat_id, example_id, 'points', 'pts')
    with zipfile.open(subpath) as fp:
        pts = parse_pts(fp)
    return np.array(pts, dtype=dtype)


def _main():
    from path import get_zip_file
    from expert_verified import get_expert_point_labels, get_seg_image
    from expert_verified import example_ids_with_expert_labels
    from points_label import get_point_labels
    from shapenet.core.meshes import get_mesh_dataset
    import matplotlib.pyplot as plt
    from mayavi import mlab
    # example_id = '1a04e3eab45ca15dd86060f189eb133'

    def vis_all(zipfile, cat_id, example_id):
        points = get_points(zipfile, cat_id, example_id)
        expert_labels = get_expert_point_labels(zipfile, cat_id, example_id)
        labels = get_point_labels(zipfile, cat_id, example_id)
        image = get_seg_image(zipfile, cat_id, example_id)
        print(len(points))

        with get_mesh_dataset(cat_id) as mesh_ds:
            example = mesh_ds[example_id]
            vertices, faces = (np.array(example[k]) for k in
                               ('vertices', 'faces'))

        def vis(vertices, faces, points, labels):
            x, z, y = vertices.T
            mlab.triangular_mesh(x, y, z, faces, color=(1, 1, 1))
            mlab.triangular_mesh(
                x, y, z, faces, color=(0, 0, 0), representation='wireframe')

            n = np.max(labels) + 1
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
            colors = colors[:n]
            for i, c in enumerate(colors):
                x, z, y = points[labels == i].T
                mlab.points3d(x, y, z, color=c, opacity=0.8, scale_factor=0.02)

        print(np.min(points, axis=0), np.max(points, axis=0))
        print(np.min(vertices, axis=0), np.max(vertices, axis=0))
        mlab.figure()
        vis(vertices, faces, points, expert_labels)
        mlab.figure()
        vis(vertices, faces, points, labels)
        plt.imshow(image)
        plt.show(block=False)
        mlab.show()
        plt.close()

    cat_id = '02691156'
    print('cat_id: %s' % cat_id)
    with get_zip_file() as f:
        example_ids = example_ids_with_expert_labels(f, cat_id)
        for example_id in example_ids:
            print('example_id: %s' % example_id)
            vis_all(f, cat_id, example_id)


if __name__ == '__main__':
    _main()
