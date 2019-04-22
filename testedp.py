# pylint: disable=missing-docstring
from __future__ import print_function

import copy
import math
import string
import time
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

    def test_wp7to8(self):
        with open('WP7TO8.txt') as f:
            dist = Distance(string.join(f.readlines()))
            a, b = dist.best_path()
            self.assertAlmostEquals(18253.201664304757, a)
            self.assertIsNotNone(b)
            self.maxDiff = None
            self.assertListEqual(['Sagittarius A*',
                                  'Phua Aub VY-S e3-3899',
                                  'Phua Aub MX-U e2-7396',
                                  'Phua Aub SJ-R e4-8234',
                                  'GRS 1739-278',
                                  'Juenae OX-U e2-8852',
                                  'Eok Bluae GX-K d8-1521',
                                  'G2 Dust Cloud Sector JH-V c2-2851',
                                  'Phipoea WK-E d12-1374',
                                  'Phipoea HJ-D c27-5254',
                                  'Dryau Chrea DB-F d11-3866',
                                  'Rothaei SI-B e2047',
                                  'Braisio FR-V e2-293',
                                  'Lyaisae HA-A e3363',
                                  'Eorl Broae EB-O e6-1507',
                                  'Rhuedgie KN-T e3-721',
                                  'Hypiae Phyloi LR-C D22',
                                  'Swoals IL-Y e0'],
                                  [each.name for each in b])

    def test_wp8to9(self):
        with open('WP8TO9.txt') as f:
            dist = Distance(string.join(f.readlines()))
            a, b = dist.best_path()
            self.assertAlmostEquals(15033.802876313275, a)
            self.assertIsNotNone(b)
            self.assertListEqual(['Goliath\'s Rest',
                                  '_Hot Temptation',
                                  '_The Remnants Trio',
                                  '_Gaesous Twins',
                                  '_Arach Nebula',
                                  'Iris\' Missive',
                                  'Blue Rhapsody Nebula',
                                  'Forgotten Twins Nebula',
                                  'Dances with Giants',
                                  'Cerulean Tranquility'],
                                  [each.alias for each in b])

    def test_wp9to10(self):
        with open('WP9TO10.txt') as f:
            dist = Distance(string.join(f.readlines()))
            a, b = dist.best_path()
            self.assertAlmostEquals(9587.24516209, a)
            self.assertIsNotNone(b)
            self.assertListEqual([u'Cerulean Tranquility',
                                  u'_Undine Haven',
                                  u'_The Briar Patch Nebula',
                                  u'The Zinnia Haze',
                                  u'Hydrangea Nebula',
                                  u'Magnus Nebula',
                                  u'_Infinite Bonds',
                                  u'Neighbouring Necklaces',
                                  u'_Eos Nebula',
                                  u'Morphenniel Nebula'],
                                  [each.alias for each in b])

    def test_wp10to11(self):
        with open('WP10TO11.txt') as f:
            dist = Distance(string.join(f.readlines()))
            a, b = dist.best_path()
            self.assertAlmostEquals(31590.10519345, a)
            self.assertIsNotNone(b)
            self.assertListEqual([u'Morphenniel Nebula',
                                  u'_Rendezvous Point',
                                  u'Aristo',
                                  u'_Phoenix Nebula',
                                  u"_Poseidon's Fury",
                                  u'Kalipheron',
                                  u'_Misty Mountains of Byeia Free',
                                  u'_Hula Hoop',
                                  u'_Shadow Earth',
                                  u"Luna's Shadow"],
                                  [each.alias for each in b])

    @unittest.skip('No data for 11 to 12 yet')
    def test_wp11to12(self):
        with open('WP11TO12.txt') as f:
            dist = Distance(string.join(f.readlines()))
            a, b = dist.best_path()
            self.assertAlmostEquals(31590.10519345, a)
            self.assertIsNotNone(b)
            print([each.alias for each in b])
            self.assertListEqual([u'Morphenniel Nebula',
                                  u'_Rendezvous Point',
                                  u'Aristo',
                                  u'_Phoenix Nebula',
                                  u"_Poseidon's Fury",
                                  u'Kalipheron',
                                  u'_Misty Mountains of Byeia Free',
                                  u'_Hula Hoop',
                                  u'_Shadow Earth',
                                  u"Luna's Shadow"],
                                  [each.alias for each in b])

    def test_wp7to10(self):
        arr = []
        for fname in ['WP7TO8.txt', 'WP8TO9.txt', 'WP9TO10.txt']:
            with open(fname) as f:
                arr.extend(f.readlines())

        _start = time.time()
        dist = Distance(string.join(arr))
        a, b = dist.best_path()
        _finish = time.time()
        self.assertAlmostEquals(42401.586920865564, a)
        self.assertIsNotNone(b)
        # print([each.alias for each in b])
        # must finish in a minute
        self.assertLess(_finish - _start, 42)
        self.assertListEqual(
            [u'Sagittarius A*', u'_Hengist Nebula', u'Phua Aub Archer Beta',
             u'Phua Aub Archer Epsilon', u'Phua Aub Archer Kappa',
             u'_GRS 1739-278', u'Crown Of Ice', u'Silver Highway',
             u'_G2 Dust Cloud', u'_Karkina Nebula', u'Dark Eye Nebula',
             u'_Stairway To Heaven', u'_Black Giants Nebula',
             u'_Lyaisae Juliet Nebula Cluster', u'Breakthrough Echoes',
             u'Hypiae Phyloi LR-C D22', u"Goliath's Rest", u'_Hot Temptation',
             u'_The Remnants Trio', u'_Gaesous Twins',
             u'Braisio Juliet Nebula Cluster', u'_Arach Nebula',
             u"Iris' Missive", u'Blue Rhapsody Nebula',
             u'Forgotten Twins Nebula', u'Dances with Giants',
             u'Cerulean Tranquility', u'_Undine Haven',
             u'_The Briar Patch Nebula', u'The Zinnia Haze',
             u'Hydrangea Nebula', u'Magnus Nebula', u'_Infinite Bonds',
             u'Neighbouring Necklaces', u'_Eos Nebula', u'Morphenniel Nebula'],
            [each.alias for each in b])

    def test_wp7to11(self):
        arr = []
        for fname in ['WP7TO8.txt', 'WP8TO9.txt', 'WP9TO10.txt', 'WP10TO11.txt']:
            with open(fname) as f:
                arr.extend(f.readlines())

        _start = time.time()
        dist = Distance(string.join(arr))
        raise NotImplementedError
        a, b = dist.best_path()
        _finish = time.time()
        self.assertAlmostEquals(42401.586920865564, a)
        self.assertIsNotNone(b)
        print([each.alias for each in b])
        # must finish in a minute
        self.assertLess(_finish - _start, 30)
        self.assertListEqual(
            [u'Sagittarius A*', u'_Hengist Nebula', u'Phua Aub Archer Beta',
             u'Phua Aub Archer Epsilon', u'Phua Aub Archer Kappa',
             u'_GRS 1739-278', u'Crown Of Ice', u'Silver Highway',
             u'_G2 Dust Cloud', u'_Karkina Nebula', u'Dark Eye Nebula',
             u'_Stairway To Heaven', u'_Black Giants Nebula',
             u'_Lyaisae Juliet Nebula Cluster', u'Breakthrough Echoes',
             u'Hypiae Phyloi LR-C D22', u"Goliath's Rest", u'_Hot Temptation',
             u'_The Remnants Trio', u'_Gaesous Twins',
             u'Braisio Juliet Nebula Cluster', u'_Arach Nebula',
             u"Iris' Missive", u'Blue Rhapsody Nebula',
             u'Forgotten Twins Nebula', u'Dances with Giants',
             u'Cerulean Tranquility', u'_Undine Haven',
             u'_The Briar Patch Nebula', u'The Zinnia Haze',
             u'Hydrangea Nebula', u'Magnus Nebula', u'_Infinite Bonds',
             u'Neighbouring Necklaces', u'_Eos Nebula', u'Morphenniel Nebula'],
            [each.alias for each in b])
