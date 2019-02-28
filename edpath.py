"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import hashlib
import json
import math
import os
import itertools
import time
import urllib
from collections import OrderedDict, namedtuple

import requests

API_CALL = 'https://www.edsm.net/api-v1/system'
DELAY = 3
CACHE_DIR = '.edpathcache'

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

class PathTo(object):
    """Compute path"""
    def __init__(self, path):
        self._path = path
        self.limit = 0

    @property
    def length(self):
        """Compute distance on the path"""
        if self.limit == 0:
            return sum([self._path[_i].distance_to(self._path[_i + 1])
                        for _i in range(len(self._path) - 1)])
        else:
            ret = 0
            # return as soon as sum is above
            # set limit to start using this branch
            for _i in range(len(self._path) - 1):
                ret += self._path[_i].distance_to(self._path[_i + 1])
                if ret > self.limit:
                    return ret

            return ret


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

if __name__ == '__main__':
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    # dictionary of sytem name:system coordinates
    all_systems = {}
    # dictionary of system name:system alias
    aliases = {}

    # load data
    for each in SYSTEMS:
        system = each.name
        print(system)
        _hash = hashlib.sha256(system.encode('utf-8')).hexdigest()
        base_dir = os.path.join(CACHE_DIR, _hash[0])
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)

        fname = os.path.join(base_dir, _hash[1:])
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

    # firect path from A to Z
    original_order = [x.name for x in SYSTEMS]
    start_point = all_systems[original_order[0]]
    final_point = all_systems[original_order[-1]]
    direct_path = PathTo([start_point, final_point])
    print('Direct path is %s', direct_path.length)

    # all permutations
    best_order = None
    best_len = 0
    i = itertools.permutations(original_order[1:-1])
    for each in i:
        print(each)
        perm_list = [start_point] + list([all_systems[x] for x in each]) + [final_point]
        curr_path = PathTo(perm_list)
        # set limit
        if best_len > 0:
            curr_path.limit = best_len

        curr_len = curr_path.length
        print('Current path is %s', curr_len)
        if best_len == 0 or curr_len < best_len:
            best_len = curr_len
            best_order = each

    print('-' * 60)
    print(best_len)
    print(original_order[0], [aliases[x] for x in best_order], original_order[-1])

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