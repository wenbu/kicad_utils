from numpy import array, identity
from numpy.linalg import inv
from math import radians, sin, cos

def rotateAboutPivot(px, py, rotation, rpx, rpy):
	rotatePivotTranslation = identity(3)
	rotatePivotTranslation[:2, 2] = array([rpx, rpy])

	r = radians(rotation)

	s = sin(r)
	c = cos(r)
	rotation = array([[c, -s, 0],
		              [s,  c, 0],
		              [0,  0, 1]])

	x, y, w = rotatePivotTranslation.dot(rotation)                    \
	                                .dot(inv(rotatePivotTranslation)) \
	                                .dot(array([px, py, 1]))          \
	                                .round(5)
	return (x, y)