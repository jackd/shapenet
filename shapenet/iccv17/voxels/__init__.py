from shapenet.iccv17.path import get_voxel_path
from scipy.io import loadmat


def get_shape():
    return (256, 256, 256)


def load_mat_data(voxel_path):
    return loadmat(voxel_path)['input'][0]


def get_mat_data(mode, example_id):
    return load_mat_data(get_voxel_path(mode, example_id))


if __name__ == '__main__':
    from path import get_image_path
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

    def vis_voxels():
        from mayavi import mlab
        from util3d.mayavi_vis import vis_voxels
        path = get_voxel_path('eval', 9)
        voxels = load_mat_data(path)

        vis_voxels(voxels, color=(0, 0, 1))
        mlab.show()

    vis_image()
    vis_voxels()
