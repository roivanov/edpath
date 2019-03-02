"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import random

class PathTooLong(Exception):
    pass

class PathTo(object):
    """Compute path"""
    def __init__(self, start, finish):
        # coords of the path start and finish
        self._start = start
        self._finish = finish
        # permutations count
        self.pcount = 0
        # raise count
        self.rcount = 0

        # how deep to cancel
        self.deep = []

    def length(self, poi, limit=0):
        """Compute distance on the POI path as it is"""
        if poi is None:
            poi = []
        path = [self._start] + poi + [self._finish]
        if limit == 0:
            return sum([path[_i].distance_to(path[_i + 1])
                        for _i in range(len(path) - 1)])
        else:
            ret = 0
            # return as soon as sum is above
            # set limit to start using this branch
            for _i in range(len(path) - 1):
                ret += path[_i].distance_to(path[_i + 1])
                if ret > limit:
                    raise PathTooLong

            return ret

    def best_path(self, poi):
        """
        poi - dictionary of system name:coord of all poi on the way
        """
        _best_order = []
        _best_len = 0
        # all permutations of poi systems
        i = self.emit(poi or [])
        for each in i:
            try:
                self.pcount += 1
                curr_len = self.length(list(each), limit=_best_len)
                if _best_len == 0 or curr_len < _best_len:
                    _best_len = curr_len
                    _best_order = each
            except PathTooLong:
                self.rcount += 1
                self.deep[-1] = None

        return _best_len, _best_order

    def emit(self, poi):
        """emit all premutations"""
        if len(poi) == 1:
            yield poi
        else:
            if not self.deep:
                random.shuffle(poi)

            for _n, elem in enumerate(poi):
                sub = self.emit(poi[0:_n] + poi[_n + 1:])
                my_level = len(self.deep)
                self.deep.append(sub)
                try:
                    while self.deep[my_level] is not None:
                        yield [elem] + sub.next()
                except StopIteration:
                    pass
                self.deep.pop()
