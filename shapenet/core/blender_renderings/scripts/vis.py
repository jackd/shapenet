def vis(cat, n_images, view_index=5, example_ids=None):
    import matplotlib.pyplot as plt
    from shapenet.core import cat_desc_to_id, get_example_ids
    from shapenet.core.blender_renderings.config import RenderConfig
    cat_id = cat_desc_to_id(cat)
    config = RenderConfig(n_images=n_images)
    dataset = config.get_dataset(cat_id, view_index)
    if example_ids is not None and len(example_ids) > 0:
        dataset = dataset.subset(example_ids)
    else:
        example_ids = get_example_ids(cat_id)
    with dataset:
        for example_id in example_ids:
            plt.imshow(dataset[example_id])
            plt.title(example_id)
            plt.show()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str)
    parser.add_argument('--shape', type=int, nargs=2, default=[192, 256])
    parser.add_argument('--blender_path', type=str, default='blender')
    parser.add_argument('-n', '--n_images', type=int, default=8)
    parser.add_argument('-i', '--example_ids', nargs='*')
    parser.add_argument('-v', '--view_index', default=5, type=int)
    args = parser.parse_args()

    vis(args.cat, args.n_images, args.view_index, args.example_ids)
