import os
import zipfile


def get_annot_dir():
    key = 'SHAPENET_CORE_ANNOTATIONS_PATH'
    if key in os.environ:
        dataset_dir = os.environ[key]
        if not os.path.isdir(dataset_dir):
            raise Exception('%s directory does not exist' % key)
        return dataset_dir
    else:
        raise Exception('%s environment variable not set.' % key)


annot_dir = get_annot_dir()


def get_zip_path():
    return os.path.join(annot_dir, 'shapenetcore_partanno_v0.zip')


def get_zip_file():
    return zipfile.ZipFile(get_zip_path(), 'r')


def _get_subpath(cat_id, example_id, topic, ext):
    fn = '%s.%s' % (example_id, ext)
    return os.path.join('PartAnnotation', cat_id, topic, fn)
