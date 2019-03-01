"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import hashlib
import json
import math
import os
import time
import urllib
from collections import OrderedDict

import requests

API_CALL = 'https://www.edsm.net/api-v1/system'
# be polite, delay in seconds
DELAY = 3

# cache directory
CACHE_DIR = '.edpathcache'
# number of chracters used to build cache tree
_DIR_CHAR = 2

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

class System(Coords):
    """System we travel"""
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    def __init__(self, name, alias):
        self._name = name
        self._alias = alias
        self._coords = None
        coords = self._load_coords()
        super(System, self).__init__(coords.x, coords.y, coords.z)
        print(coords)

    def _load_coords(self):
        _hash = hashlib.sha256(self._name.encode('utf-8')).hexdigest()
        base_dir = os.path.join(CACHE_DIR, _hash[:_DIR_CHAR])
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)

        fname = os.path.join(base_dir, _hash[_DIR_CHAR:])
        print(fname)
        if os.path.exists(fname):
            print('Loading from file')
            with open(fname) as f:
                data = json.load(f)
        else:
            print('Connecting to EDSM')
            params = OrderedDict([('systemName', self._name), ('showCoordinates', 1)])
            r = requests.get(API_CALL, params=urllib.urlencode(params))
            if r.status_code == 200:
                with open(fname, 'w') as f:
                    f.write(r.text)
                data = json.loads(r.text)
                time.sleep(DELAY)
            else:
                print('ERROR: status %s is not 200' % r.status_code)
                raise RuntimeError

        print(data)
        if self._name.lower() != data.get('name', '').lower() or 'coords' not in data:
            os.remove(fname)
            raise RuntimeError('Bad data')

        return Coords(**data['coords'])

    def __repr__(self):
        return 'System(name={name}, {coords})'.format(name=self._name, coords=super(System, self).__repr__())

    @property
    def name(self):
        return self._name

    @property
    def alias(self):
        return self._alias

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
        #
        if poi is None:
            poi = []
        # all permutations of poi systems
        i = self.emit(poi)
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

SYSTEMS = [System('Great Annihilator', 'Great Annihilator'),

           System('Hypoe Flyi HW-W e1-7966', 'Galionas'),
           System('HYPOE FLYI HX-T E3-295', 'Caeruleum Luna "Mysturji Crater"'),
           System('Zunuae HL-Y e6903', 'Zunuae Nebula'),
           System('Byoomao MI-S e4-5423', 'Wulfric'),
           System('Sagittarius A*', 'Sagittarius A*'),

           # visiting this system adds another 3k ly to the distance
           System('Kyli Flyuae WO-A f39', 'Dance of the Compact Quartet'),
           System('Myriesly DQ-G d10-1240', 'Insinnergy\'s World'),
           System('Myriesly RY-S e3-5414', 'Six Rings'),
           System('Myriesly CL-P e5-4186', 'Emerald Remnant'),
           System('Myriesly CL-P e5-7383', 'Fenrisulfur'),

           System('STUEMEAE KM-W C1-342', 'WP7 Altum Sagittarii'),
          ]

def run_main(path):
    print('ALL SYSTEMS:')
    print(path)

    # direct path from A to Z
    mypath = PathTo(path[0], path[-1])
    print('Direct path is %s' % mypath.length(poi=None))

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
    print(best_order)
    print(' > '.join([x.alias for x in path[:1] + best_order + path[-2:]]))
    print(mypath.pcount)

if __name__ == '__main__':
    run_main(SYSTEMS)


# 10487.3914861 ly

# 229523138 function calls (190628638 primitive calls) in 133.731 seconds
# 221822632 function calls (182928132 primitive calls) in 114.752 seconds