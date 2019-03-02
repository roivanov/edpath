from __future__ import print_function, unicode_literals

import json
import math
import time
import urllib
from collections import OrderedDict

import requests

from filecache import FileCache

API_CALL = 'https://www.edsm.net/api-v1/system'
# be polite, delay in seconds
DELAY = 3

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
        return self.__known_distances.get(other.name, None)

    def _distance_to(self, other):
        ret = super(System, self).distance_to(other)
        self.store_distance_to(other, ret)
        # this will double memory footprint
        other.store_distance_to(self, ret)
        return ret

    def distance_to(self, other):
        """Get distance to other system"""
        # 426782242 function calls (387887742 primitive calls) in 198.585 seconds
        return self.known_distance_to(other) or other.known_distance_to(self) or self._distance_to(other)
        # 365294359 function calls (326399859 primitive calls) in 177.060 seconds
        # return self.known_distance_to(other) or self._distance_to(other)

        # 139839636 function calls (100945136 primitive calls) in 79.376 seconds
        # if other.name not in self.__known_distances:
        #     ret = super(System, self).distance_to(other)
        #     self.__known_distances[other.name] = ret

        # return self.__known_distances[other.name]
