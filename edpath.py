"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import copy
import math
import random

DEBUG = False

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

        # full path as it comes in
        self.path = copy.copy(dist)

        self.pcount = 0
        self.rcount = 0

        self.level = ''

    def print(self, *args):
        if DEBUG:
            self.print(self.level, *args)

    @property
    def fact(self):
        return math.factorial(len(self.path) - 2)

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

    @property
    def len_path_asis(self):
        ret = 0
        for _i in range(len(self.path) - 1):
            ret += self.path[_i].distance_to(self.path[_i + 1])
        
        return ret

    def best_path(self, limit=0):
        # find first path A->..->Z

        first_path = self.len_path_asis
        self.print('First path len:', first_path)

        if limit == 0:
            limit = first_path

        # if no poi
        if len(self.poi) < 2:
            self.print('short path, returning')
            return first_path, self.path
        else:
            # for every poi
            best_path = copy.copy(self.path[1:])
            found_best = copy.copy(self.path)
            found_len = first_path
            self.print('starting best path # of poi:', len(best_path))

            # try all combinations (exclude finish)
            for indx in range(len(best_path) - 1):
                elem = best_path[0]
                self.print('indx', indx, elem)
                # next distance on this path (excluding self.start)
                # print(best_path)

                first_jump = self.start.distance_to(elem)
                next_limit = limit - first_jump
                self.print('first jump', first_jump, elem, 'next limit', next_limit)

                if next_limit > 0:
                    self.print('going sub path')
                    subdistance = Distance(best_path)
                    subdistance.level = self.level + '  '
                    sub_best_len, sub_best_path = subdistance.best_path(next_limit)

                    if first_jump + sub_best_len < limit:
                        self.print('path looks like shorter' , self.start, sub_best_path)
                        limit = first_jump + sub_best_len
                        found_len = limit
                        found_best = copy.copy([self.start] + sub_best_path)
                    else:
                        self.print('path is not shorter')

                if indx < len(best_path) - 1:
                    best_path[0], best_path[indx + 1] = best_path[indx + 1], best_path[0]
            
            self.print('BP:', found_len, found_best)
            # assert len(best_path) == len(self.poi), len(self.poi)
            # assert best_path is not None

            return found_len, found_best
