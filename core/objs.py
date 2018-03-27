import os
from path import get_zip_path
import dids.file_io.zip_file_dataset as zfd


def get_obj_file_dataset(cat_id):
    """Get a DIDS dataset mapping example_ids to obj file objects."""
    dataset = zfd.ZipFileDataset(get_zip_path(cat_id))

    def key_fn(example_id):
        return os.path.join(cat_id, example_id, 'model.obj')

    def inverse_key_fn(path):
        subpaths = path.split('/')
        if len(subpaths) == 3 and subpaths[2][-4:] == '.obj':
            return subpaths[1]
        else:
            return None

    dataset = dataset.map_keys(key_fn, inverse_key_fn)
    return dataset
