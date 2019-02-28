"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals
from collections import namedtuple
import json
import hashlib
import os

EXAMPLE = 'https://www.edsm.net/api-v1/system?systemName=Merope&showCoordinates=1'
SYSTEMS = ['Merope']
DATA = '{"name":"Merope","coords":{"x":-78.59375,"y":-149.625,"z":-340.53125},"coordsLocked":true}'
CACHE_DIR = '.edpathcache'

class Coords(namedtuple('Coords', 'x y z')):
    pass

if __name__ == '__main__':
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

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
            data = json.loads(DATA)
            with open(fname, 'w') as f:
                f.write(DATA)

        print(data)
        coords = Coords(**data['coords'])
        print(coords)
