# pylint: disable=missing-docstring
from __future__ import print_function

import copy
import math
import unittest

from edpath import Distance
from edsystems import Coords, System


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
        mypath = Distance([x, z, y])
        self.assertAlmostEqual(math.sqrt(3), mypath.direct_length)
        self.assertEqual(0, mypath.pcount)

        mypath = Distance([z, x, y])
        self.assertAlmostEqual(math.sqrt(81+361+841), mypath.direct_length)
        self.assertEqual(0, mypath.pcount)

    def test_one_poi(self):
        x = Coords(0, 0, 0)
        y = Coords(1, 1, 1)
        z = Coords(10, 20, 30)

        mypath = Distance([x, z, y])
        self.assertAlmostEqual(math.sqrt(3), mypath.direct_length)
        self.assertEqual(0, mypath.pcount)

        self.assertAlmostEqual(math.sqrt(100+400+900), x.distance_to(z))
        self.assertAlmostEqual(math.sqrt(81+361+841), z.distance_to(y))

        mypath = Distance([x, z, y])
        self.assertAlmostEqual(math.sqrt(100+400+900)+math.sqrt(81+361+841), mypath.len_path_asis)
        self.assertEqual(0, mypath.pcount)

    def test_two_poi(self):
        x = Coords(0, 0, 0)
        y = Coords(1, 1, 1)
        z = Coords(10, 20, 30)
        a = Coords(100, 200, 300)

        mypath = Distance([x, z, a, y])
        self.assertAlmostEqual(math.sqrt(3), mypath.direct_length)
        self.assertEqual(0, mypath.pcount)

        self.assertAlmostEqual(math.sqrt(100+400+900), x.distance_to(z))
        self.assertAlmostEqual(math.sqrt(90**2+180**2+270**2), z.distance_to(a))
        self.assertAlmostEqual(math.sqrt(99**2+199**2+299**2), a.distance_to(y))

        mypath = Distance([x, z, a, y])
        self.assertAlmostEqual(math.sqrt(100+400+900) + 
                               math.sqrt(90**2+180**2+270**2) +
                               math.sqrt(99**2+199**2+299**2),
                               mypath.len_path_asis)
        self.assertEqual(0, mypath.pcount)

    def test_two_poi_best_path(self):
        x = System(name='x', coords=Coords(0, 0, 0))
        y = System(name='y', coords=Coords(1, 1, 1))
        z = System(name='z', coords=Coords(10, 20, 30))
        a = System(name='a', coords=Coords(100, 200, 300))

        mypath = Distance([x, y])
        self.assertAlmostEqual(math.sqrt(3), mypath.direct_length)
        self.assertEqual(0, mypath.pcount)

        self.assertAlmostEqual(math.sqrt(100+400+900), x.distance_to(z))
        self.assertAlmostEqual(math.sqrt(90**2+180**2+270**2), z.distance_to(a))
        self.assertAlmostEqual(math.sqrt(99**2+199**2+299**2), a.distance_to(y))

        mypath = Distance([x, a, z, y])
        best_len, best_order = mypath.best_path()
        print(best_len, best_order)
        self.assertAlmostEqual(math.sqrt(100+400+900) + 
                               math.sqrt(90**2+180**2+270**2) +
                               math.sqrt(99**2+199**2+299**2),
                               best_len)
        
        # self.assertEqual(2, mypath.pcount)

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

    def test_saga_three(self):
        s = '''Sagittarius A*
Phua Aub Archer Beta - GalMap Ref: Phua Aub VY-S e3-3899
Phua Aub Archer Epsilon - GalMap Ref: Phua Aub MX-U e2-7396
#Phua Aub Archer Kappa - GalMap Ref: Phua Aub SJ-R e4-8234
'''
        dist = Distance(s)

        self.assertEqual(3, len(dist))
        self.assertAlmostEquals(1117.0375812871348, dist.direct_length)
        self.assertAlmostEquals(1388.475446592071, dist.len_path_asis)
        a, b = dist.best_path()
        self.assertAlmostEquals(1388.475446592071, a)
        self.assertListEqual(['Sagittarius A*',
                              'Phua Aub Archer Beta',
                              'Phua Aub Archer Epsilon'],
                              [x.alias for x in b])

    def test_saga_four(self):
        s = '''Sagittarius A*
Phua Aub Archer Beta - GalMap Ref: Phua Aub VY-S e3-3899
Phua Aub Archer Epsilon - GalMap Ref: Phua Aub MX-U e2-7396
Phua Aub Archer Kappa - GalMap Ref: Phua Aub SJ-R e4-8234
'''
        dist = Distance(s)

        self.assertEqual(4, len(dist))
        self.assertAlmostEquals(1569.8244630297245, dist.direct_length)
        self.assertAlmostEquals(1851.5503574292647, dist.len_path_asis)
        a, b = dist.best_path()
        self.assertAlmostEquals(1851.5503574292647, a)
        self.assertListEqual(['Sagittarius A*',
                              'Phua Aub Archer Beta',
                              'Phua Aub Archer Epsilon',
                              'Phua Aub Archer Kappa'],
                              [x.alias for x in b])

    def test_saga_seven(self):
        s = '''Sagittarius A*
Phua Aub Archer Beta - GalMap Ref: Phua Aub VY-S e3-3899
Phua Aub Archer Epsilon - GalMap Ref: Phua Aub MX-U e2-7396
Phua Aub Archer Kappa - GalMap Ref: Phua Aub SJ-R e4-8234
Hengist Nebula - GalMap Ref: Juenae OX-U e2-8852_
GRS 1739-278 - GalMap Ref: GRS 1739-278_
Karkina Nebula - GalMap Ref: Eok Bluae GX-K d8-1521_

'''
        dist = Distance(s)

        self.assertEqual(7, len(dist))
        self.assertAlmostEquals(2175.5414924005127, dist.direct_length)
        self.assertAlmostEquals(8018.37276782833, dist.len_path_asis)
        a, b = dist.best_path()
        self.assertAlmostEquals(6456.316604972468, a)
        self.assertListEqual(['Sagittarius A*',
                              'Phua Aub Archer Beta',
                              'Phua Aub Archer Epsilon',
                              'Phua Aub Archer Kappa',
                              '_GRS 1739-278',
                              '_Hengist Nebula',
                              '_Karkina Nebula',
                              ],
                              [x.alias for x in b])
