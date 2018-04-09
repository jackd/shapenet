if __name__ == '__main__':
    from shapenet.core import get_cat_ids
    from shapenet.core.meshes import remove_empty_meshes
    for cat_id in get_cat_ids():
        remove_empty_meshes(cat_id)
