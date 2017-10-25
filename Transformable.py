from abc import ABCMeta, abstractmethod

class Transformable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def transform(self, t = (0, 0), r = 0, rp = (0, 0)):
        """Transform this node using the supplied values.
        Transformation order is RT. Scaling is not supported.

        Keyword arguments:
        t -- translation vector
        r -- rotation, in degrees. Note that KiCAD's rotation direction is clockwise.
        rp -- rotation pivot

        All of these default to zero.
        """
        pass
