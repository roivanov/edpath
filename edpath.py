"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import copy
import math
import random
from collections import namedtuple

from edsystems import mSystem

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
        # swap: system marked with * is the real start
        for indx, elem in enumerate(self.path):
            if '*' in elem.alias:
                self.path[0], self.path[indx] = self.path[indx], self.path[0]
                break

        # path counted until the end
        self.pcount = 0

        # path rejected early
        self.rcount = 0

        self.level = 0
        # we need this value for the case when we skip minor poi
        self.poi_len = len(self.path) - 2

    def print(self, *args):
        if DEBUG:
            self.print('' * self.level, *args)

    @staticmethod
    def print_path(best_path):
        COLS = ('Name', 'Next', 'Path', 'Last')
        Table = namedtuple('Table', COLS)
        Table.__new__.__defaults__ = ('-',) * len(COLS)

        table = [Table(*COLS)]

        for n, curr in enumerate(best_path):
            if n < len(best_path) - 1:
                to_last = Distance(best_path[n:])
                table.append(Table(curr.alias,
                                   '{: 5.2f} ly'.format(curr.distance_to(best_path[n + 1])),
                                   '{: 5.2f} ly'.format(to_last.len_path_asis),
                                   '{: 5.2f} ly'.format(to_last.direct_length)
                                   ))
            else:
                table.append(Table(curr.alias))

        tlen = [0] * len(COLS)
        for each in table:
            for indx, elem in enumerate(each):
                tlen[indx] = max(tlen[indx], len(elem))

        sep = ['-' * each for each in tlen]
        table.append(sep)
        table.insert(0, sep)
        table.insert(2, sep)

        for each in table:
            s = '| '
            for indx, elem in enumerate(each):
                s += ' %s |' %elem.center(tlen[indx])
            print(s)

    def print_stats(self):
        print('Total %d! combinations' % self.poi_len)
        print('Paths considered: %d, paths rejected early %d' % (self.pcount, self.rcount))
        total = math.factorial(self.poi_len)
        print('Paths not even considered: %d of %d' % (total - self.rcount - self.pcount, total))
        print('Optmizitaion %.1f (more is better)' % (100.0 * self.rcount / total))

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

    def best_path(self, limit=0, skip_minor=False):
        # find first path A->..->Z

        first_path = self.len_path_asis
        self.print('First path len:', first_path)

        if limit == 0:
            limit = first_path

        # if no poi
        if len(self.poi) < 2:
            self.pcount += 1
            self.print('short path, returning')
            return first_path, self.path
        else:
            # for every poi
            tpath = self.path[1:-1]
            if skip_minor:
                tpath = [x for x in tpath if not isinstance(x, mSystem)]
                self.poi_len = len(tpath)

            if self.level == 0:
                random.shuffle(tpath)

            found_best = [self.path[0]] + tpath + [self.path[-1]]

            best_path = copy.copy(found_best[1:])
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
                    subdistance.level = self.level + 2
                    sub_best_len, sub_best_path = subdistance.best_path(next_limit)

                    self.pcount += subdistance.pcount
                    self.rcount += subdistance.rcount

                    if first_jump + sub_best_len < limit:
                        self.print('path looks like shorter', self.start, sub_best_path)
                        limit = first_jump + sub_best_len
                        found_len = limit
                        found_best = copy.copy([self.start] + sub_best_path)
                    else:
                        self.print('path is not shorter')
                else:
                    # reject all sub path when first jump is too long (minus start, finish, elem)
                    self.rcount += math.factorial(len(self.path) - 3)

                if indx < len(best_path) - 1:
                    best_path[0], best_path[indx + 1] = best_path[indx + 1], best_path[0]

            self.print('BP:', found_len, found_best)
            # assert len(best_path) == len(self.poi), len(self.poi)
            # assert best_path is not None

            return found_len, found_best
