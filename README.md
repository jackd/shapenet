This repository provides python loading, manipulation and caching functions for interacting with the [ShapeNet](https://www.shapenet.org/) dataset.

Dependencies:
* [Dictionary Interface to Datasets (DIDS)](https://github.com/jackd/dids)
* [util3d](https://github.com/jackd/util3d)

# Setup
1. Install pip dependencies
```bash
pip install numpy h5py progress wget
```
2. Clone relevant repositories
```bash
cd /path/to/parent_dir
git clone https://github.com/jackd/dids.git
git clone https://github.com/jackd/util3d.git
git clone https://github.com/jackd/shapenet.git
```
3. Add parent directory to `PYTHONPATH`
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/parent_dir
```
Consider adding this to your `~/.bashrc` file if you do not want to call it for each new terminal.
4. Copy `default_config.yaml` to `config.yaml` and make changes depending on where you have data saved etc. See comments in `default_config.yaml` for more.
```bash
cd shapenet
cp default_config.yaml config.yaml
gedit config.yaml  # make changes
```

## Core Dataset
We cannot provide data for the core dataset - see the [dataset website](https://www.shapenet.org/) for access.

Assign the location of your the ShapeNet dataset to the `SHAPENET_CORE_PATH` environment variable,
```
export SHAPENET_CORE_PATH=/path/to/ShapeNetCore.v1
```
This directory should contain the zip files for each category, e.g. `02691156.zip` should contain all `obj` files for planes.

## ICCV 2017 Competition Dataset
To use functions associated with the ICCV2017 competition dataset, after downloading the data,
```
export SHAPENET17_PATH=/path/to/shapenet2017/dataset
```
Currently this only supports uncompressed data. This directory should contain `train_imgs`, `test_images`, `train_voxels`, `train_imgs`, `val_imgs` and `val_voxels` directories as provided by the dataset. This may change in the future to support compressed versions.

# Data
Most data is provided via a [DIDS](https://github.com/jackd/dids) Dataset. A number of these datasets are saved to disk as required to reduce repeated calculations. These should be calculated and saved as required, but you can manually force the data preprocessing. For example, the following will generate meshes, point clouds and voxels for the plane category in the core dataset with default arguments.

```
cd core
cd meshes/scripts
python generate_mesh_data.py plane   # parses objs to hdf5 vertices/faces
cd ../../point_clouds/scripts
python create_point_clouds.py plane  # samples faces of meshes
cd ../../voxels/scripts
python create_voxels.py plane        # creates voxels in binvox format
python create_archive.py plane       # zip the binvox files created above
```

Resulting datasets can be used much like dictionaries, though are required to be explicitly opened or used in a `with` block.

```
import numpy as np
from shapenet.core.meshes import get_mesh_dataset
from shapenet.core import cat_desc_to_id
from util3d.mayavi_vis import vis_mesh
from mayavi import mlab

desc = 'plane'

cat_id = cat_desc_to_id(desc)
with get_mesh_dataset(cat_id) as mesh_dataset:
    for example_id in mesh_dataset:
        example_group = mesh_dataset[example_id]
        vertices, faces = (
            np.array(example_group[k]) for k in ('vertices', 'faces'))
        vis_mesh(vertices, faces, color=(0, 0, 1), axis_order='xzy')
        mlab.show()
```

See [examples](https://github.com/jackd/shapenet/tree/master/example) for more.
