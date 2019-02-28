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

SYSTEMS = ['Great Annihilator',
           'Hypoe Flyi HW-W e1-7966',
           'HYPOE FLYI HX-T E3-295',
           'STUEMEAE KM-W C1-342']

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

if __name__ == '__main__':
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    all_systems = {}

    # load data
    for system in SYSTEMS:
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

    print(all_systems)

    # firect path from A to Z
    direct_path = all_systems[SYSTEMS[0]].distance_to(all_systems[SYSTEMS[-1]])
    print('Direct path is %s', direct_path)

    # path in the order of systems
    best_order = SYSTEMS
    best_path = sum([all_systems[SYSTEMS[i]].distance_to(all_systems[SYSTEMS[i+1]]) for i in range(len(SYSTEMS) - 1)])
    print('First path is %s', best_path)

    # all permutations
    i = itertools.permutations(SYSTEMS[1:-1])
    for each in i:
        print(each)
        perm_list = [SYSTEMS[0]] + list(each) + [SYSTEMS[-1]]
        print(perm_list)
        curr_path = sum([all_systems[perm_list[i]].distance_to(all_systems[perm_list[i+1]]) for i in range(len(perm_list) - 1)])
        print('Current path is %s', curr_path)
        if curr_path < best_path:
            best_path = curr_path
            best_order = perm_list
    
    print('-' * 60)
    print(best_path)
    print(best_order)
