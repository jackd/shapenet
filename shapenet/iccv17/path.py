import os


def get_dataset_dir():
    if 'SHAPENET17_PATH' in os.environ:
        dataset_dir = os.environ['SHAPENET17_PATH']
        if not os.path.isdir(dataset_dir):
            raise Exception('SHAPENET17_PATH directory does not exist')
        return dataset_dir
    else:
        raise Exception('SHAPENET17_PATH environment variable not set.')


def get_image_shape():
    return (192, 256, 3)


def _mode(mode):
    return 'val' if mode == 'eval' else mode


def _example_id(example_id):
    return '%06d' % example_id if isinstance(example_id, int) else example_id


def _image_id(image_id):
    return ('%03d' % image_id) if isinstance(image_id, int) else image_id


def get_all_images_dir(mode):
    return os.path.join(get_dataset_dir(), '%s_imgs' % _mode(mode))


def get_example_images_dir(mode, example_id):
    return os.path.join(get_all_images_dir(mode), _example_id(example_id))


def get_example_ids(mode):
    return os.listdir(get_all_images_dir(_mode(mode)))


def n_images(mode, example_id):
    return len(os.listdir(get_example_images_dir(mode, example_id)))


def get_image_path(mode, example_id, image_id):
    filename = '%s.png' % _image_id(image_id)
    return os.path.join(get_example_images_dir(mode, example_id), filename)


def get_example_indices(mode):
    return (int(k) for k in get_example_ids(mode))


def get_all_voxels_dir(mode):
    return os.path.join(get_dataset_dir(), '%s_voxels' % _mode(mode))


def get_voxel_path(mode, example_id):
    return os.path.join(
        get_all_voxels_dir(mode), _example_id(example_id), 'model.mat')


if __name__ == '__main__':
    mode = 'eval'
    example_id = 9

    def vis_image():
        import matplotlib.pyplot as plt
        from scipy.misc import imread
        image_idx = 0
        image = imread(get_image_path(mode, example_id, image_idx))
        image = image[..., :3]
        plt.imshow(image)
        plt.figure()
        plt.imshow(image[..., -1])
        plt.show()

    vis_image()
