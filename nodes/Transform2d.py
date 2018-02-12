'''
Functions for transforming 2D points.
'''
from math import radians, sin, cos
from abc import ABCMeta, abstractmethod
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

def transform(list_of_transformables, t=(0,0), r=0, rp=(0,0)):
    for transformable in list_of_transformables:
        transformable.transform(t, r, rp)

def transform_point(x, y, t=(0,0), r=0, rp=(0,0)):
    T = get_translation_matrix(t=t)
    R = get_rotation_matrix(r=r, rp=rp)
    transform = T.dot(R)

    return tuple(transform.dot(array([x, y, 1])).round(5)[:2])

class Transformable(object):
    '''
    ABC for a class that can be transformed.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def transform(self, t = (0, 0), r = 0, rp = (0, 0)):
        """Transform this node using the supplied values.
        Transformation order is RT. Scaling is not supported.

        Keyword arguments:
        t -- translation vector
        r -- counterclockwise rotation, in degrees
        rp -- rotation pivot

        All of these default to zero.
        """
        pass
