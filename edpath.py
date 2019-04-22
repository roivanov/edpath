# -*- coding: utf-8 -*-
"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import copy
import datetime
import json
import math
import random
import threading
import time
import warnings
from collections import namedtuple

from edsystems import System, mSystem
from filecache import NoCache, FileCache, MemCache

DEBUG = False
DEBUG_LEVELS = [0]

# Tunables
THREADS = False
# when start split into half. 5 is the optimal
SPLIT_LOW_LIMIT = 5

CACHE_TYPE = {0: NoCache,
              1: MemCache,
              2: FileCache}


class _T_Distance(threading.Thread):
    def __init__(self, dist):
        super(_T_Distance, self).__init__()
        assert isinstance(dist, Distance)
        self._dist = dist
        self.best = None

    def run(self):
        self.best = self._dist.best_path()


COLS = ('Name', 'Next', 'Path', 'Last')
Table = namedtuple('Table', COLS)
Table.__new__.__defaults__ = ('-',) * len(COLS)


class _BaseDistance(MemCache):
    """
    Distance from A to B with every POI unique (no duplicates)
    """
    def __init__(self, dist, name=None):
        self.name = name

        assert isinstance(dist, list)
        if len(dist) < 2:
            raise ValueError('distance must be two or more poi')

        self._path = copy.copy(dist)

        # swap: system marked with * is the real start
        # for indx, elem in enumerate(self.path):
        #     if '*' in elem.alias:
        #         # self.path[0], self.path[indx] = self.path[indx], self.path[0]
        #         break

        # Cache tunables (len of poi)
        CACHE_MIN = 3
        CACHE_MAX = 36

        # set file cache
        if CACHE_MIN <= len(self.poi) <= CACHE_MAX:
            arr = [self.start.name] + sorted([each.name for each in self.poi]) + [self.finish.name]
            cache_name = ';'.join(arr)
        else:
            cache_name = None

        super(_BaseDistance, self).__init__(cache_name=cache_name)

        # path counted until the end
        self.pcount = 0

        # path rejected early
        self.rcount = 0

        self.level = 0
        # we need this value for the case when we skip minor poi
        self.poi_len = len(self) - 2

    def print(self, *args):
        if DEBUG and self.level in DEBUG_LEVELS:
            print(' ' * self.level, *args)

    @staticmethod
    def _make_table(path):
        table = [Table(*COLS)]

        for n, curr in enumerate(path):
            if n < len(path) - 1:
                to_last = _BaseDistance(path[n:])
                table.append(Table(curr.alias,
                                   '{: 5.2f} ly'.format(curr.distance_to(path[n + 1])),
                                   '{: 5.2f} ly'.format(to_last.len_path_asis),
                                   '{: 5.2f} ly'.format(to_last.direct_length)
                                   ))
            else:
                table.append(Table(curr.alias))

        return table

    @staticmethod
    def _make_tlen(table):
        tlen = [0] * len(COLS)
        for each in table:
            for indx, elem in enumerate(each):
                tlen[indx] = max(tlen[indx], len(elem))

        return tlen

    @staticmethod
    def print_path(best_path):
        table = _BaseDistance._make_table(best_path)
        tlen = _BaseDistance._make_tlen(table)
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
        return self._path[0]

    @property
    def finish(self):
        return self._path[-1]

    @property
    def poi(self):
        return self._path[1:-1]

    @property
    def path(self):
        return self._path

    @property
    def direct_length(self):
        return self.start.distance_to(self.finish)

    def __iter__(self):
        for _i in range(len(self) - 1):
            yield (self._path[_i], self._path[_i + 1])

    @property
    def len_path_asis(self):
        return sum([a.distance_to(b) for (a, b) in self])

    def best_path(self, limit=0):
        # find first path A->..->Z

        # if no poi
        if len(self) <= 3:
            self.pcount += 1
            self.print('short path, returning')
            return self.len_path_asis, self._path
        else:
            f = self.read()

            start = time.time()
            if f:
                return self.from_dict(json.loads(f))
            elif len(self) > SPLIT_LOW_LIMIT:
                found_len, found_best = self.__best_path_with_split()
            else:
                found_len, found_best = self.__best_path(limit)
            finish = time.time()

            if found_best:
                self.save(json.dumps(self.to_dict(found_len,
                                                  found_best)),
                          time_spent=((finish - start) * math.factorial(self.len_poi)))

            return found_len, found_best

    def from_dict(self, data):
        found_len = data['found_len']
        found_best = []
        for each in data['found_best']:
            system = [x for x in self._path if x.name == each]
            try:
                assert len(system) == 1, each
            except AssertionError:
                print(system)
                raise
            found_best.append(system[0])

        return found_len, found_best

    def to_dict(self, path_len, path):
        return {'found_len': path_len,
                'found_best': [x.name for x in path]}

    def __getitem__(self, key):
        return self._path[key]

    def __setitem__(self, key, value):
        self._path[key] = value

    def _swap(self, key1, key2):
        self[key1], self[key2] = self[key2], self[key1]

    def __best_path(self, limit=0):
        # for every poi
        found_best = None

        self.print('Starting with path len:', self.len_path_asis)
        if limit == 0:
            limit = self.len_path_asis
            found_best = copy.copy(self.path)

        # this array we try all combinations
        sub_path = _BaseDistance(self._path[1:])
        sub_path.level = self.level + 2

        self.print('starting best path # of len:', len(sub_path))

        # try all combinations (exclude finish)
        for indx in range(1, len(sub_path)):
            self.print('indx', indx, sub_path.start)
            # next distance on this path (excluding self.start)
            # print(best_path)

            first_jump = self.start.distance_to(sub_path.start)

            if first_jump < limit:
                self.print('going sub path, first_jump= %.2f' % first_jump)
                sub_best_len, sub_best_path = sub_path.best_path(limit - first_jump)

                self.pcount += sub_path.pcount
                self.rcount += sub_path.rcount

                if first_jump + sub_best_len < limit and sub_best_path:
                    self.print('path looks like shorter', self.start, sub_best_path)
                    limit = first_jump + sub_best_len
                    found_best = copy.copy([self.start] + sub_best_path)
                else:
                    self.print('path is not shorter')
            else:
                # reject all sub path when first jump is too long (minus start, finish, elem)
                self.rcount += math.factorial(len(self._path) - 3)

            if indx < len(sub_path) - 1:
                sub_path._swap(0, indx)

        self.print('BP:', limit, found_best)

        return limit, found_best

    @staticmethod
    def __with_threads(p_one, p_two):
        if len(p_one) >= len(p_two):
            # spawn separate thread for longest distance
            # use current thread for short one
            t_one = _T_Distance(p_one)
            t_one.start()

            path_two = p_two.best_path()[-1]

            t_one.join()
            path_one = t_one.best[-1]
        else:
            path_two, path_one = _BaseDistance.__with_threads(p_two, p_one)

        return path_one, path_two

    @staticmethod
    def join(a, b):
        assert a is not None
        assert b is not None
        assert a[-1] == b[0]

        return _BaseDistance(a + b[1:])

    def split(self, position):
        p_one = _BaseDistance(self._path[:position + 1])
        p_one.level = self.level + 2
        p_two = _BaseDistance(self._path[position:])
        p_two.level = self.level + 2

        return p_one, p_two

    def slice(self, start, finish=-1):
        raise NotImplementedError
        sub_path = _BaseDistance(self._path[start:finish])
        sub_path.level = self.level + 2

        return sub_path

    def _left_right_range(self, l):
        middle = l/2
        yield middle
        i = 1
        val = middle
        while 0 < val < l:
            val = middle - i
            if 2 <= val:
                yield val
            val = middle + i
            if val < l - 2:
                yield val
            i += 1

    def _seq_range(self, l):
        return range(2, l - 2)

    def __best_path_with_split(self):
        ret = {}

        for each in self.poi:
            a, b = self.start.distance_to(each), self.finish.distance_to(each)
            # this will remove duplicates!!!
            ret[a / (a + b)] = each

        scaled_distance = _BaseDistance([self.start] +
                                        [ret[k] for k in sorted(ret.keys())] +
                                        [self.finish])
        best_l = 0
        best_best = None
        for indx in self._seq_range(len(scaled_distance)):
            _start = time.time()
            p_one, p_two = scaled_distance.split(position=indx)
            if self.level == 0:
                ratio = '%d/%d' % (len(p_one), len(p_two))
            else:
                ratio = None
            assert len(p_one) > 2 and len(p_two) > 2, ratio

            if THREADS and min([len(p_one), len(p_two)]) > THREADS:
                test_path = _BaseDistance.join(*self.__with_threads(p_one, p_two))
            else:
                test_path = _BaseDistance.join(p_one.best_path()[-1],
                                               p_two.best_path()[-1])
            
            _elapsed = time.time() - _start
            if ratio and _elapsed > 1:
                print(ratio, ('Elapsed: %s' % str(datetime.timedelta(seconds=_elapsed)).split('.')[0]))

            l = test_path.len_path_asis
            if best_l == 0 or l < best_l:
                best_l = l
                best_best = copy.copy(test_path.path)
                if ratio:
                    print(ratio, l)

        return best_l, best_best

    def __add__(self, other):
        assert isinstance(other, _BaseDistance)
        if self.finish == other.start:
            return _BaseDistance(self._path + other.path[1:])
        else:
            return _BaseDistance(self._path + other.path)

    def __len__(self):
        return len(self._path)

    @property
    def len_poi(self):
        return len(self._path) - 2


class Distance(_BaseDistance):
    def __init__(self, dist, name=None, skip_minor=False):
        data = []

        if isinstance(dist, list):
            data = copy.copy(dist)
        elif isinstance(dist, str):
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
                        data.append(s(name=arr[0]))
                    else:
                        data.append(s(name=arr[0], alias=arr[1]))
        else:
            raise ValueError('Unsupported type')

        if len(data) < 2:
            raise ValueError('distance must be two or more poi')

        # remove duplicates as it confuses load_from_json
        dedup = [data[0], data[-1]]
        for each in data[1:-1]:
            if each not in dedup:
                dedup.append(each)

        assert len(data) >= len(dedup)
        data = [dedup[0]] + [x for x in dedup[2:]] + [dedup[1]]

        if skip_minor:
            assert not isinstance(data, mSystem)
            assert not isinstance(data, mSystem)
            data = [data[0]] + [x for x in data[1:-1]
                                if not isinstance(x, mSystem)] + [data[-1]]
        else:
            # To set a limit
            # self._path = copy.copy(data[:37])
            data = copy.copy(data)
            # :32           seq mc15:   1:55 (47087) 41MB
            #                ng mc15:   1:54
            # :33           seq mc15:   2:55 (37229)
            #               seq mc20:   0:52 (38082)
            # :34           seq mc20:   1:10 (41042)
            #               seq mc21:   0:55 (41102)
            #               seq mc22:   0:53 (41142)
            # :35           seq mc22:   1:31 (51890)
            #               seq mc23:   1:03 (51937) 45MB
            #               seq mc24:   1:04 (51970)
            #             seq mc4-24:   1:09 (45027) 43MB
            # :36           seq mc24:   1:15 (56550)
            #               seq mc25:   1:12 (56583) 48MB
            #               seq mc26:   1:14 (56606)
            # :37           seq mc26:   1:13
            # oo            seq mc26:   1:10
            #               seq mc28:   1:07
            #               seq mc32:   1:06

        super(Distance, self).__init__(data, name)

    def best_path(self, limit=0):
        self.shuffle_poi()
        return super(Distance, self).best_path(limit)

    def shuffle_poi(self):
        if len(self) > 3:
            tpath = self.poi
            random.shuffle(tpath)
            self._path = [self.start] + tpath + [self.finish]


class MultiDistance(object):
    def __init__(self, *args):
        self.distances = []
        for each in args:
            if isinstance(each, Distance):
                self.distances.append(each)
            else:
                self.distances.append(Distance(each))

    @property
    def direct_length(self):
        return self.distances[0].start.distance_to(self.distances[-1].finish)

    @staticmethod
    def print_path(best_path):
        Distance.print_path(best_path)

    def best_path_with_split(self):
        best_len = 0
        meta_dist = None
        separate_at = []
        for indx, distance in enumerate(self.distances):
            assert isinstance(distance, Distance)
            a, b = distance.best_path()

            best_len += a

            if meta_dist:
                if meta_dist.finish != distance.start:
                    best_len += meta_dist.finish.distance_to(distance.start)
                meta_dist += Distance(b)
            else:
                meta_dist = Distance(b)

            separate_at.append(len(meta_dist))

        return best_len, meta_dist.path
