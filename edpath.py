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
from collections import OrderedDict, namedtuple

import requests

API_CALL = 'https://www.edsm.net/api-v1/system'
# be polite, delay in seconds
DELAY = 3

# cache directory
CACHE_DIR = '.edpathcache'
# number of chracters used to build cache tree
_DIR_CHAR = 2

class Coords(namedtuple('Coords', 'x y z')):
    """XYZ coordinates"""
    def distance_to(self, other):
        """compute distance between two points"""
        assert isinstance(other, Coords)
        return math.sqrt(sum([math.pow(self.x - other.x, 2),
                              math.pow(self.y - other.y, 2),
                              math.pow(self.z - other.z, 2)]))

class System(namedtuple('System', 'name alias')):
    """System we travel"""
    pass

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
        poi_list = poi.keys()
        # all permutations of poi system names
        i = self.emit(poi_list)
        for each in i:
            try:
                curr_len = self.length(list([poi[x] for x in each]), limit=_best_len)
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

def run_main(syst_list):
    # dictionary of sytem name:system coordinates
    all_systems = {}
    # dictionary of system name:system alias
    aliases = {}

    # load data
    for each in syst_list:
        system = each.name
        print(system)
        _hash = hashlib.sha256(system.encode('utf-8')).hexdigest()
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
            params = OrderedDict([('systemName', system), ('showCoordinates', 1)])
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
        if system.lower() != data.get('name', '').lower() or 'coords' not in data:
            os.remove(fname)
            raise RuntimeError('Bad data')

        coords = Coords(**data['coords'])
        print(coords)
        all_systems[system] = coords
        aliases[system] = each.alias

    print('ALL SYSTEMS:')
    print(all_systems)

    # all system names in original order
    original_order = [x.name for x in syst_list]
    # direct path from A to Z
    mypath = PathTo(all_systems[original_order[0]], all_systems[original_order[-1]])
    print('Direct path is %s' % mypath.length(poi=None))

    import cProfile, pstats, StringIO
    pr = cProfile.Profile()
    pr.enable()
    best_len, best_order = mypath.best_path({sys: all_systems[sys] for sys in original_order[1:-1]})
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

    print('-' * 60)
    print(best_len)
    print(' > '.join(original_order[:1] + [aliases[x] for x in best_order] + original_order[-2:]))
    print(mypath.pcount)
    # assert mypath.pcount in [362880, 3628800, 42523300, 38894560], 'troubled permutation'

if __name__ == '__main__':
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)
    run_main(SYSTEMS)


# 10487.3914861
# Great Annihilator [u'Zunuae Nebula',
#                    u'Caeruleum Luna "Mysturji Crater"',
#                    u'Galionas',
#                    u'Dance of the Compact Quartet',
#                    u'Six Rings',
#                    u'Wulfric',
#                    u'Emerald Remnant',
#                    u'Fenrisulfur',
#                    u"Insinnergy's World",
#                    u'Sagittarius A*'] STUEMEAE KM-W C1-342

# using sum
# python edpath.py  130.30s user 0.70s system 99% cpu 2:11.46 total
# tail  48.58s user 0.63s system 37% cpu 2:11.46 total

# using for loop and eject
# python edpath.py  105.36s user 0.46s system 99% cpu 1:46.05 total
# tail  60.99s user 0.67s system 58% cpu 1:46.05 total

# python edpath.py  79.96s user 0.36s system 99% cpu 1:20.48 total
# tail  46.56s user 0.52s system 58% cpu 1:20.48 total
