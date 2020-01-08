import numpy as np


def segment(points, segmentation):
    n = np.max(segmentation) + 1
    seg_points = [points[segmentation == i] for i in range(n)]
    return seg_points
