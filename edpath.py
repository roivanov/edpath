"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function
import json

EXAMPLE = 'https://www.edsm.net/api-v1/system?systemName=Merope&showCoordinates=1'
SYSTEMS = ['Merope']
DATA = '{"name":"Merope","coords":{"x":-78.59375,"y":-149.625,"z":-340.53125},"coordsLocked":true}'

class Coords():
    pass

if __name__ == '__main__':
    print(SYSTEMS)
    print(json.loads(DATA))
