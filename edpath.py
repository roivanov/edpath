"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import copy
import math
import random

class Distance(object):
    """
    D1: A->B->C->D->Z
        +--+          first jump
           +--------+ subdistance.best_len
    D2:    B->C->D->Z or
           B->D->C->Z
    D3:       C->D->Z
    D4:          D->Z
    """
    def __init__(self, dist):
        if len(dist) < 2:
            raise ValueError('distance must be two or more poi')
        self.path = dist

        self.fact = math.factorial(len(self.poi))
        self.pcount = 0
        self.rcount = 0

    @property
    def start(self):
        return self.path[0]

    @property
    def finish(self):
        return self.path[-1]

    @property
    def poi(self):
        return self.path[1:-1]

    @property
    def direct_length(self):
        return self.start.distance_to(self.finish)

    def best_path(self, limit=0):
        # find first path A->..->Z
        # import pdb
        # pdb.set_trace()
        first_path = []
        for _i in range(len(self.path) - 1):
            first_path.append(self.path[_i].distance_to(self.path[_i + 1]))

        assert len(self.path) - len(first_path) == 1
        print('First path:', first_path)

        if limit == 0:
            limit = sum(first_path)

        if len(self.poi) < 2:
            return sum(first_path), [self.start ] + self.poi + [self.finish]
        else:
            # for every poi
            best_path = copy.copy(self.poi)

            # try all combinations            
            for indx in range(len(self.poi)):
                elem = self.poi[0]
                first_jump = self.start.distance_to(elem)
                next_limit = limit - first_jump
                if next_limit > 0:
                    subdistance = Distance(self.poi + [self.finish])
                    sub_best_len, sub_best_path = subdistance.best_path(next_limit)

                    if first_jump + sub_best_len < limit:
                        limit = first_jump + sub_best_len
                        best_path = sub_best_path
                # else:
                #     print('Jump from %s to %s it long')

                # try next element
                if indx < len(self.poi) - 1:
                    self.poi[0], self.poi[indx + 1] = self.poi[indx + 1], self.poi[0]
            
            print('BP:', limit, best_path + [self.finish])
            assert len(best_path) == len(self.poi), len(self.poi)
            assert best_path is not None

            return limit, [self.start] + best_path + [self.finish]
