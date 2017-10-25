'''
Functions for transforming 2D points.
'''
from math import radians, sin, cos
from numpy import array, identity
from numpy.linalg import inv

# pylint: disable=invalid-name, bad-whitespace, unused-variable

def rotate_about_pivot(px, py, rotation, rpx, rpy):
    '''
    Rotate a point (px, py) about the point (rpx, rpy) by rotation degrees.
    '''
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

def get_rotation_matrix(r = 0, rp = (0, 0)):
    '''
    Get a transformation matrix for the specified rotation of r degrees
    about a pivot point rp.
    '''
    '''
    rp_matrix = identity(3)
    rp_matrix[:2, 2] = array(rp)
    '''
    rp_matrix = get_translation_matrix(t = rp)

    # r is negated because of KiCAD's rotation direction
    r = -radians(r)

    s = sin(r)
    c = cos(r)
    r_matrix = array([[c, -s, 0],
                      [s,  c, 0],
                      [0,  0, 1]])

    return rp_matrix.dot(r_matrix).dot(inv(rp_matrix))

def get_translation_matrix(t = (0, 0)):
    '''
    Get a transformation matrix for the specified translation t.
    '''
    t_matrix = identity(3)
    t_matrix[:2, 2] = array(t)
    return t_matrix
