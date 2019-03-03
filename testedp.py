# pylint: disable=missing-docstring
from __future__ import print_function

import copy
import math
import unittest

from edpath import PathTo
from edsystems import Coords


class TestEDPath(unittest.TestCase):
    def test_distance(self):
        x = Coords(0, 0, 0)
        y = Coords(1, 1, 1)
        z = Coords(10, 20, 30)
        self.assertAlmostEqual(math.sqrt(3), x.distance_to(y))
        self.assertAlmostEqual(math.sqrt(81+361+841), y.distance_to(z))

    def test_direct_path(self):
        x = Coords(0, 0, 0)
        y = Coords(1, 1, 1)
        z = Coords(10, 20, 30)
        mypath = PathTo(x, y)
        self.assertAlmostEqual(math.sqrt(3), mypath.length(poi=None))
        self.assertEqual(0, mypath.pcount)

        mypath = PathTo(z, y)
        self.assertAlmostEqual(math.sqrt(81+361+841), mypath.length(poi=None))
        self.assertEqual(0, mypath.pcount)

    def test_one_poi(self):
        x = Coords(0, 0, 0)
        y = Coords(1, 1, 1)
        z = Coords(10, 20, 30)

        mypath = PathTo(x, y)
        self.assertAlmostEqual(math.sqrt(3), mypath.length(poi=None))
        self.assertEqual(0, mypath.pcount)

        self.assertAlmostEqual(math.sqrt(100+400+900), x.distance_to(z))
        self.assertAlmostEqual(math.sqrt(81+361+841), z.distance_to(y))

        mypath = PathTo(x, y)
        self.assertAlmostEqual(math.sqrt(100+400+900)+math.sqrt(81+361+841), mypath.length(poi=[z]))
        self.assertEqual(0, mypath.pcount)

    def test_two_poi(self):
        x = Coords(0, 0, 0)
        y = Coords(1, 1, 1)
        z = Coords(10, 20, 30)
        a = Coords(100, 200, 300)

        mypath = PathTo(x, y)
        self.assertAlmostEqual(math.sqrt(3), mypath.length(poi=None))
        self.assertEqual(0, mypath.pcount)

        self.assertAlmostEqual(math.sqrt(100+400+900), x.distance_to(z))
        self.assertAlmostEqual(math.sqrt(90**2+180**2+270**2), z.distance_to(a))
        self.assertAlmostEqual(math.sqrt(99**2+199**2+299**2), a.distance_to(y))

        mypath = PathTo(x, y)
        self.assertAlmostEqual(math.sqrt(100+400+900) + 
                               math.sqrt(90**2+180**2+270**2) +
                               math.sqrt(99**2+199**2+299**2),
                               mypath.length(poi=[z, a]))
        self.assertEqual(0, mypath.pcount)

    def test_two_poi_best_path(self):
        x = Coords(0, 0, 0)
        y = Coords(1, 1, 1)
        z = Coords(10, 20, 30)
        a = Coords(100, 200, 300)

        mypath = PathTo(x, y)
        self.assertAlmostEqual(math.sqrt(3), mypath.length(poi=None))
        self.assertEqual(0, mypath.pcount)

        self.assertAlmostEqual(math.sqrt(100+400+900), x.distance_to(z))
        self.assertAlmostEqual(math.sqrt(90**2+180**2+270**2), z.distance_to(a))
        self.assertAlmostEqual(math.sqrt(99**2+199**2+299**2), a.distance_to(y))

        mypath = PathTo(x, y)
        best_len, best_order = mypath.best_path(poi=[a, z])
        print(best_len, best_order)
        self.assertAlmostEqual(math.sqrt(100+400+900) + 
                               math.sqrt(90**2+180**2+270**2) +
                               math.sqrt(99**2+199**2+299**2),
                               best_len)
        
        self.assertEqual(2, mypath.pcount)

    def test_fast_tree(self):
        arr = [1, 2, 3, 4]
        amap = list(range(len(arr)))
        dest = copy.copy(arr)

        """
        (1, 2, 3, 4)
        (1, 2, 4, 3)
        (1, 3, 2, 4)
        (1, 3, 4, 2)
        """
        print(arr)
        print(dest)
        i = len(dest) - 1
        dest[i], dest[i-1] = dest[i-1], dest[i]
        print(dest)

        print(amap)
        from itertools import permutations
        perm = permutations(arr)
        print(perm)
        # for each in perm:
            # print(each)

        self.assertSetEqual(set(arr), set(dest), 'Lost some values')
        self.assertEqual(1, 1)
