import os
import numpy as np
from path import _get_subpath, get_zip_path
from shapenet.image import load_image_from_zip
from io_util import parse_seg
import dids.file_io.zip_file_dataset as zfd


class SegmentedDataset(zfd.ZipFileDataset):
    def __init__(self, cat_id):
        super(SegmentedDataset, self).__init__(get_zip_path())
        self._cat_id = cat_id

    def keys(self):
        if not self.open:
            raise RuntimeError('Cannot check keys of closed dataset.')
        return example_ids_with_expert_labels(self._file, self._cat_id)


class SegmentedPointCloudDataset(SegmentedDataset):
    def __getitem__(self, key):
        with self._file.open(_label_path(self._cat_id, key)) as fp:
            data = parse_seg(fp)
        return np.array(data)


class SegmentedImageDataset(SegmentedDataset):
    def __getitem__(self, key):
        topic = os.path.join('expert_verified', 'seg_img')
        subpath = _get_subpath(self._cat_id, key, topic, 'png')
        return load_image_from_zip(self._file, subpath)


def _label_path(cat_id, example_id):
    topic = os.path.join('expert_verified', 'points_label')
    return _get_subpath(cat_id, example_id, topic, 'seg')


def has_expert_labels(zipfile, cat_id, example_id):
    try:
        with zipfile.open(_label_path(cat_id, example_id)):
            pass
        return True
    except KeyError:
        return False


def example_ids_with_expert_labels(zipfile, cat_id):
    base_path = os.path.join(
        'PartAnnotation', cat_id, 'expert_verified', 'points_label')
    n = len(base_path)
    return [name[n+1:-4] for name in zipfile.namelist()
            if name.startswith(base_path) and len(name) > n+1]


def get_expert_point_labels(zipfile, cat_id, example_id):
    with zipfile.open(_label_path(cat_id, example_id)) as fp:
        point_labels = parse_seg(fp)

    data = np.array(point_labels, dtype=np.uint8)
    return data


def get_seg_image(zipfile, cat_id, example_id):
    topic = os.path.join('expert_verified', 'seg_img')
    subpath = _get_subpath(cat_id, example_id, topic, 'png')
    return load_image_from_zip(zipfile, subpath)


def _main():
    # from path import get_zip_file
    from dids import Dataset
    import matplotlib.pyplot as plt
    cat_id = '02691156'
    example_id = '1a04e3eab45ca15dd86060f189eb133'
    ds = Dataset.zip(
        SegmentedImageDataset(cat_id), SegmentedPointCloudDataset(cat_id))
    with ds:
        image, cloud = ds[example_id]
        print(cloud.shape)
        print(cloud.dtype)
        plt.imshow(image)
        plt.show()
    # with get_zip_file() as f:
        # print(np.min(get_expert_point_labels(f, cat_id, example_id)))

        # image = get_seg_image(f, cat_id, example_id)
        # plt.imshow(image)
        # plt.show()


if __name__ == '__main__':
    _main()
