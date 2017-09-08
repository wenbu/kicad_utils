from math import radians, sin, cos
from numpy import array, identity
from numpy.linalg import inv

def rotate_about_pivot(px, py, rotation, rpx, rpy):
    """Rotate a point (px, py) about the point (rpx, rpy) by rotation degrees."""
    rotate_pivot_matrix = identity(3)
    rotate_pivot_matrix[:2, 2] = array([rpx, rpy])

    r = radians(rotation)

    s = sin(r)
    c = cos(r)
    rotation = array([[c, -s, 0],
                      [s,  c, 0],
                      [0,  0, 1]])

    x, y, w = rotate_pivot_matrix.dot(rotation)                 \
                                 .dot(inv(rotate_pivot_matrix)) \
                                 .dot(array([px, py, 1]))       \
                                 .round(5)
    return (x, y)