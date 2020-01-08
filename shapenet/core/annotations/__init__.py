from expert_verified import get_seg_image, get_expert_point_labels
from expert_verified import has_expert_labels
from points import get_points
from points_label import get_point_labels
from path import get_zip_file
import benchmark
from segment import segment


def get_best_point_labels(zipfile, cat_id, example_id):
    if has_expert_labels(zipfile, cat_id, example_id):
        return get_expert_point_labels(zipfile, cat_id, example_id)
    else:
        return get_point_labels(zipfile, cat_id, example_id)


__all__ = [
    get_seg_image,
    get_expert_point_labels,
    get_point_labels,
    get_points,
    get_zip_file,
    segment,
    has_expert_labels,
    benchmark,
]
