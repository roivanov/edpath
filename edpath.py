# -*- coding: utf-8 -*-
"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import copy
import json
import math
import random
import threading
from collections import namedtuple

from edsystems import System, mSystem
from filecache import FileCache

DEBUG = False
THREADS = True

class _T_Distance(threading.Thread):
    def __init__(self, dist):
        assert isinstance(dist, Distance)
        self._dist = dist
        self.best = None
        threading.Thread.__init__(self)

    def run(self):
        self.best = self._dist.best_path()


class Distance(FileCache):
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
        if isinstance(dist, list):
            pass
        elif isinstance(dist, str):
            new_dist = []
            for each in dist.splitlines():
                each = each.decode('utf-8').strip()
                if each and each[0] != '#':
                    each = each.replace('–', '-')
                    if '- GalMap Ref:' in each:
                        each = each.replace('- GalMap Ref:', '/')
                        arr = [x.strip() for x in each.split('/', 2)]
                        arr.reverse()
                    else:
                        arr = [x.strip() for x in each.split('/', 2)]
                    
                    # add as mSystem when name or alias starts or ends with _
                    s = System
                    for indx, elem in enumerate(arr):
                        if elem[0] == '_' or elem[-1] == '_':
                            s = mSystem
                            arr[indx] = elem.strip('_ ')

                    if len(arr) == 1 or arr[0] == arr[1]:
                        new_dist.append(s(name=arr[0]))
                    else:
                        new_dist.append(s(name=arr[0], alias=arr[1]))
            dist = new_dist
        else:
            raise ValueError('Unsupported type')

        if len(dist) < 2:
            raise ValueError('distance must be two or more poi')

        # full path as it comes in
        self.path = copy.copy(dist)
        # swap: system marked with * is the real start
        # for indx, elem in enumerate(self.path):
        #     if '*' in elem.alias:
        #         # self.path[0], self.path[indx] = self.path[indx], self.path[0]
        #         break

        # set file cache
        if len(self.poi) > 6:
            arr = [self.start.name] + sorted([each.name for each in self.poi]) + [self.finish.name]
            self.fname = ';'.join(arr)
        else:
            self.fname = None

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
        return Distance.__get_length(self.path)

    @staticmethod
    def __get_length(path):
        return sum([path[_i].distance_to(path[_i + 1]) for _i in range(len(path) - 1)])

    def best_path(self, limit=0, skip_minor=False):
        # find first path A->..->Z

        first_path = Distance.__get_length(self.path)
        self.print('First path len:', first_path)

        if limit == 0:
            limit = first_path

        # if no poi
        if len(self.poi) < 2:
            self.pcount += 1
            self.print('short path, returning')
            return first_path, self.path
        else:
            with self.open() as f:
                if f:
                    return self.from_dict(json.load(f))
                else:
                    found_len, found_best = self._best_path(first_path, limit, skip_minor)
                    self.save(json.dumps(self.to_dict(found_len, found_best)))

                    return found_len, found_best

    def from_dict(self, data):
        found_len = data['found_len']
        found_best = []
        for each in data['found_best']:
            system = [x for x in self.path if x.name == each]
            assert len(system) == 1, each
            found_best.append(system[0])

        return found_len, found_best

    def to_dict(self, path_len, path):
        return {'found_len': path_len,
                'found_best': [x.name for x in path]}

    def _best_path(self, first_path, limit, skip_minor):
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

    def scale(self):
        ret = {}
        for each in self.path[1:-1]:
            a, b = self.start.distance_to(each), self.finish.distance_to(each)
            scale = a / (a + b)
            ret[scale] = each

        ret = [ret[k] for k in sorted(ret.keys())]
        return ret

    def best_path_with_split(self, skip_minor=False):
        with self.open() as f:
            if f:
                return self.from_dict(json.load(f))
            else:
                scaled = self.scale()
                middle = len(scaled) / 2

                best_l = 0
                best_best = None
                # FIXME N might need better logic
                N = min(3, middle)
                for n in range(-N, N + 1):
                    p_one = Distance([self.start] + scaled[:middle + n +1])
                    p_two = Distance(scaled[middle + n:] + [self.finish])
                    if THREADS:
                        t_one = _T_Distance(p_one)
                        t_two = _T_Distance(p_two)
                        t_one.start()
                        t_two.start()
                        t_one.join()
                        t_two.join()
                        path_one = t_one.best[-1]
                        path_two = t_two.best[-1]
                    else:
                        path_one = p_one.best_path(skip_minor=skip_minor)[-1]
                        path_two = p_two.best_path(skip_minor=skip_minor)[-1]

                    assert path_one[-1] == path_two[0]

                    test_path = path_one + path_two[1:]
                    l = Distance.__get_length(test_path)
                    if best_l == 0 or l < best_l:
                        best_l = l
                        best_best = copy.copy(test_path)
                        print(n, l, path_two[0].alias, len(path_one), len(path_two))
                
                self.save(json.dumps(self.to_dict(best_l, best_best)))

                return best_l, best_best
