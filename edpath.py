"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import hashlib
import json
import math
import random
import os
import time
import urllib
from contextlib import contextmanager
from collections import OrderedDict

import requests

API_CALL = 'https://www.edsm.net/api-v1/system'
# be polite, delay in seconds
DELAY = 3

class FileCache(object):
    """File Cache of the objects or data"""

    # cache directory
    CACHE_DIR = '.edpathcache'
    # number of chracters used to build cache tree
    _DIR_CHAR = 2

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    def __init__(self, utf8_encoded_name):
        self.__fname = FileCache.set_fname(utf8_encoded_name)
        print(self.__fname)
        raise NotImplementedError

    @staticmethod
    def set_fname(utf8_encoded_name):
        _hash = hashlib.sha256(utf8_encoded_name).hexdigest()
        base_dir = os.path.join(FileCache.CACHE_DIR, _hash[:FileCache._DIR_CHAR])
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)

        return os.path.join(base_dir, _hash[FileCache._DIR_CHAR:])

    @property
    def fname(self):
        return self.__fname

    @fname.setter
    def fname(self, value):
        self.__fname = FileCache.set_fname(value)

    def save(self, data):
        with open(self.fname, 'w') as f:
            f.write(data)

    @contextmanager
    def open(self):
        if os.path.exists(self.fname):
            # print('Loading from file')
            with open(self.fname) as f:
                yield f
        else:
            yield None

    def remove(self):
        os.remove(self.fname)


class Coords(object):
    """XYZ coordinates"""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def distance_to(self, other):
        """compute distance between two points"""
        assert isinstance(other, Coords)
        return math.sqrt(sum([math.pow(self.x - other.x, 2),
                              math.pow(self.y - other.y, 2),
                              math.pow(self.z - other.z, 2)]))

    def __repr__(self):
        return 'Coords(x={x}, y={y}, z={z})'.format(x=self.x, y=self.y, z=self.z)

class System(Coords, FileCache):
    """System we travel"""
    def __init__(self, name, alias=None, coords=None):
        self._name = name
        self._alias = alias or name

        if coords is None:
            coords = self._load_coords()
        super(System, self).__init__(coords.x, coords.y, coords.z)
        self.__known_distances = {}

    def _load_coords(self):
        self.fname = self._name.encode('utf-8')

        with self.open() as f:
            if f:
                data = json.load(f)
            else:
                print('Connecting to EDSM')
                params = OrderedDict([('systemName', self._name), ('showCoordinates', 1)])
                r = requests.get(API_CALL, params=urllib.urlencode(params))
                if r.status_code == 200:
                    self.save(r.text)
                    data = json.loads(r.text)
                    time.sleep(DELAY)
                else:
                    print('ERROR: status %s is not 200' % r.status_code)
                    raise RuntimeError

        # print(data)
        if self._name.lower() != data.get('name', '').lower() or 'coords' not in data:
            self.remove()
            raise RuntimeError('Bad data')

        return Coords(**data['coords'])

    def __repr__(self):
        return 'System(name={name}, {coords})'.format(name=self._name, coords=super(System, self).__repr__())

    @property
    def name(self):
        """Get system name"""
        return self._name

    @property
    def alias(self):
        """Get system alias"""
        return self._alias

    def store_distance_to(self, other, value):
        """Cache distance to other system"""
        self.__known_distances[other.name] = value

    def known_distance_to(self, other):
        """Retrieve distance to other system from cache"""
        self.__known_distances.get(other.name, None)

    def _distance_to(self, other):
        ret = super(System, self).distance_to(other)
        self.store_distance_to(other, ret)
        return ret

    def distance_to(self, other):
        """Get distance to other system"""
        # 426782242 function calls (387887742 primitive calls) in 198.585 seconds
        # return self.known_distance_to(other) or other.known_distance_to(self) or self._distance_to(other)
        # 365294359 function calls (326399859 primitive calls) in 177.060 seconds
        # return self.known_distance_to(other) or self._distance_to(other)

        # 139839636 function calls (100945136 primitive calls) in 79.376 seconds
        if other.name not in self.__known_distances:
            ret = super(System, self).distance_to(other)
            self.__known_distances[other.name] = ret

        return self.__known_distances[other.name]

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

        # how deep to cancel
        self.deep = []

    def length(self, poi, limit=None):
        """Compute distance on the POI path as it is"""
        if poi is None:
            poi = []
        path = [self._start] + poi + [self._finish]
        if limit is None:
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
        _best_len = None
        # all permutations of poi systems
        i = self.emit(poi or [])
        for each in i:
            try:
                curr_len = self.length(list(each), limit=_best_len)
                self.pcount += 1
                if _best_len is None or curr_len < _best_len:
                    _best_len = curr_len
                    _best_order = each
            except PathTooLong:
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
                self.deep.append(sub)
                my_level = len(self.deep) - 1
                try:
                    while self.deep[my_level] is not None:
                        yield [elem] + sub.next()
                except StopIteration:
                    pass
                self.deep.pop()

SYSTEMS = [System('Great Annihilator'),

           System('Zunuae HL-Y e6903', 'Zunuae Nebula'),
           System('Hypoe Flyi HW-W e1-7966', 'Galionas'),
           System('HYPOE FLYI HX-T E3-295', 'Caeruleum Luna "Mysturji Crater"'),
           System('Byoomao MI-S e4-5423', 'Wulfric'),
           System('Sagittarius A*'),

           # visiting this system adds another 3k ly to the distance
           System('Kyli Flyuae WO-A f39', '*** Dance of the Compact Quartet'),
           System('Myriesly DQ-G d10-1240', 'Insinnergy\'s World'),
           System('Myriesly RY-S e3-5414', 'Six Rings'),
           System('Myriesly CL-P e5-4186', 'Emerald Remnant'),
           System('Myriesly CL-P e5-7383', 'Fenrisulfur'),

           System('STUEMEAE KM-W C1-342', 'WP7 Altum Sagittarii'),
          ]

def run_main(path):
    # direct path from A to Z
    mypath = PathTo(path[0], path[-1])
    print('Direct path is %.2f ly' % mypath.length(poi=None))

    import cProfile, pstats, StringIO
    pr = cProfile.Profile()
    pr.enable()
    best_len, best_order = mypath.best_path(poi=path[1:-1])
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

    print('-' * 60)
    print(best_len)
    best_path = path[:1] + best_order + path[-2:]

    i = iter(best_path)
    curr = None
    nxt = i.next()
    n = 0
    while nxt:
        try:
            curr = nxt
            nxt = i.next()
        except StopIteration:
            nxt = None

        to_last = PathTo(curr, best_path[-1])
        print('  ' * n,
              curr.alias,
              ' > %.2f ly to next' % curr.distance_to(nxt or curr),
              ' >> %.2f ly to last by poi' % to_last.length(poi=best_path[n+1:-1]),
              ' >>> %.2f ly to last directly' % to_last.length(poi=[]),
              )
        n += 1

    print(mypath.pcount)

if __name__ == '__main__':
    run_main(SYSTEMS)


# 10487.3914861 ly

# 229523138 function calls (190628638 primitive calls) in 133.731 seconds
# 221822632 function calls (182928132 primitive calls) in 114.752 seconds
# with store len
# 139839636 function calls (100945136 primitive calls) in 84.637 seconds
# with store len both ways
# 139839459 function calls (100944959 primitive calls) in 85.496 seconds
# 426782242 function calls (387887742 primitive calls) in 198.585 seconds
