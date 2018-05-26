import os
import string
import path
import zipfile


def get_config_id(shape, n_images):
    shape_str = string.join((str(s) for s in shape), '-')
    return 'r%s_%d' % (shape_str, n_images)


def parse_config_id(config_id):
    shape_str, n_images = config_id[1:].split('_')
    n_images = int(n_images)
    shape = tuple(int(s) for s in shape_str.split('-'))
    return dict(shape=shape, n_images=n_images)


class RenderConfig(object):
    def __init__(self, shape=(192, 256), n_images=8, config_id=None):
        self._shape = shape
        self._n_images = n_images
        self._id = get_config_id(shape, n_images) if config_id is None \
            else config_id

    @staticmethod
    def from_id(config_id):
        args = parse_config_id(config_id)
        return RenderConfig(args['shape'], args['n_images'], config_id)

    @property
    def config_id(self):
        return self._id

    @property
    def shape(self):
        return self._shape

    @property
    def n_images(self):
        return self._n_images

    def view_angle(self, view_index):
        return view_index * 360 // self._n_images

    @property
    def root_dir(self):
        return path.get_renderings_dir(self.config_id)

    def get_zip_path(self, cat_id):
        return os.path.join(self.root_dir, '%s.zip' % cat_id)

    def get_zip_file(self, cat_id, mode='r'):
        return zipfile.ZipFile(self.get_zip_path(cat_id), mode=mode)

    def has_zip_file(self, cat_id):
        return os.path.isfile(self.get_zip_path(cat_id))

    def get_cat_dir(self, cat_id):
        return path.get_cat_dir(self.config_id, cat_id)

    def get_example_dir(self, cat_id, example_id):
        return path.get_example_dir(self.config_id, cat_id, example_id)

    def _path(self, subpath):
        return os.path.join(self.root_dir, subpath)

    def get_example_image_subpath(self, cat_id, example_id, view_angle):
        return path.get_example_image_subpath(
            cat_id, example_id, view_angle)

    def get_example_normals_subpath(self, cat_id, example_id, view_angle):
        return path.get_example_normals_subpath(cat_id, example_id, view_angle)

    def get_example_albedo_path(self, cat_id, example_id, view_angle):
        return path.get_example_albedo_subpath(cat_id, example_id, view_angle)

    def get_example_depth_subpath(self, cat_id, example_id, view_angle):
        return path.get_example_depth_subpath(cat_id, example_id, view_angle)

    def get_multi_view_dataset(
                self, cat_id, view_indices=None, example_ids=None, mode='r'):
        from shapenet.image import load_image_from_file
        from dids.file_io.zip_file_dataset import ZipFileDataset
        if view_indices is None:
            view_indices = range(self.n_images)
            view_angles = [self.view_angle(i) for i in view_indices]
        else:
            view_angles = {i: self.view_angle(i) for i in view_indices}

        def key_fn(key):
            example_id, view_index = key
            view_angle = view_angles[view_index]
            return self.get_example_image_subpath(
                cat_id, example_id, view_angle)

        dataset = ZipFileDataset(self.get_zip_path(cat_id), mode)
        dataset = dataset.map(load_image_from_file)
        dataset = dataset.map_keys(key_fn)
        if example_ids is not None:
            keys = []
            for example_id in example_ids:
                keys.extend((example_id, k) for k in view_indices)
            dataset = dataset.subset(keys)
        return dataset

    def get_dataset(self, cat_id, view_index, example_ids=None, mode='r'):
        from shapenet.image import load_image_from_file
        from dids.file_io.zip_file_dataset import ZipFileDataset
        view_angle = self.view_angle(view_index)

        def key_fn(example_id):
            return self.get_example_image_subpath(
                cat_id, example_id, view_angle)

        def inverse_key_fn(path):
            subpaths = path.split('/')
            if len(subpaths) == 3:
                i = subpaths[1]
                p0 = self.get_example_image_subpath(cat_id, i, view_angle)
                if path == p0:
                    return i
            return None

        dataset = ZipFileDataset(self.get_zip_path(cat_id), mode)
        dataset = dataset.map(load_image_from_file)
        dataset = dataset.map_keys(key_fn, inverse_key_fn)
        if example_ids is not None:
            dataset = dataset.subset(example_ids)
        return dataset


if __name__ == '__main__':
    # import numpy as np
    import matplotlib.pyplot as plt
    from shapenet.core import cat_desc_to_id
    # from zipfile import ZipFile
    # from shapenet.image import load_image_from_zip
    from shapenet.image import with_background
    cat_desc = 'plane'
    cat_id = cat_desc_to_id(cat_desc)
    view_index = 5
    config = RenderConfig()
    with config.get_dataset(cat_id, view_index) as ds:
        for k, v in ds.items():
            plt.imshow(with_background(v, 255))
            plt.title(k)
            plt.show()
    # with ZipFile(config.get_zip_path(cat_id)) as zf:
    #     for i in range(config.n_images):
    #         subpath = config.get_example_image_subpath(
    #             cat_id, example_id, config.view_angle(i))
    #         image = load_image_from_zip(zf, subpath)
    #
    #         plt.figure()
    #         plt.imshow(np.array(image)[..., :3])
    #         image = with_background(image, 255)
    #         plt.figure()
    #         plt.imshow(image)
    #         plt.show()
