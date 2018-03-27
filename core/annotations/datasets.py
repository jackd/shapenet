import os
import numpy as np
import dids.file_io.zip_file_dataset as zfd
from shapenet.image import load_image_from_zip
from path import get_zip_path
from points import get_points
from io_util import parse_seg
from expert_verified import _label_path, _get_subpath
from expert_verified import has_expert_labels


class _AnnotationsDataset(zfd.ZipFileDataset):
    def __init__(self, cat_id):
        super(_AnnotationsDataset, self).__init__(get_zip_path())
        self._cat_id = cat_id

    def __contains__(self, key):
        return has_expert_labels(self._file, self._cat_id, key)


class PointCloudDataset(_AnnotationsDataset):
    def __getitem__(self, key):
        return get_points(self._file, self._cat_id, key)


class SegmentationDataset(_AnnotationsDataset):
    def __getitem__(self, key):
        with self._file.open(_label_path(self._cat_id, key)) as fp:
            data = parse_seg(fp)
        return np.array(data, np.int32)


class SegmentedImageDataset(_AnnotationsDataset):
    def __getitem__(self, key):
        topic = os.path.join('expert_verified', 'seg_img')
        subpath = _get_subpath(self._cat_id, key, topic, 'png')
        return load_image_from_zip(self._file, subpath)


def _main(cat_id, example_id):
    from dids import Dataset
    import matplotlib.pyplot as plt
    from util3d.mayavi_vis import vis_point_cloud
    from mayavi import mlab

    colors = (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 1, 1),
    )

    image_ds = SegmentedImageDataset(cat_id)
    pc_ds = PointCloudDataset(cat_id)
    s_ds = SegmentationDataset(cat_id)
    ds = Dataset.zip(image_ds, pc_ds, s_ds)
    with ds:
        image, pc, s = ds[example_id]
        print(np.min(s))
        print(np.max(s))
        ns = np.max(s) + 1
        plt.imshow(image)
        for i in range(ns-1):
            cloud = pc[s == i+1]
            color = colors[i % len(colors)]
            vis_point_cloud(cloud, color=color, scale_factor=0.02)
        plt.show(block=False)
        mlab.show()


if __name__ == '__main__':
    cat_id = '02691156'
    example_id = '1a04e3eab45ca15dd86060f189eb133'
    _main(cat_id, example_id)
