"""Example usage:
```bash
python generate_point_clouds.py rifle -s=1024
```
"""

def generate_point_cloud_data(cat_desc, samples, normals, overwrite=False):
    from shapenet.core import cat_desc_to_id
    from shapenet.core.point_clouds import generate_point_cloud_data

    cat_id = cat_desc_to_id(cat_desc)
    generate_point_cloud_data(cat_id, samples, normals, overwrite=overwrite)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cat', type=str, nargs='+')
    parser.add_argument('-s', '--samples', type=int, help='number of samples')
    parser.add_argument('-n', '--normals', action='store_true')
    parser.add_argument('-o', '--overwrite', action='store_true')

    args = parser.parse_args()
    for cat in args.cat:
        generate_point_cloud_data(
            cat, args.samples, args.normals, args.overwrite)
