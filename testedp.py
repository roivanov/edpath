import unittest
import math
from edpath import Coords

class TestEDPath(unittest.TestCase):
    def test_distance(self):
        x = Coords(0, 0, 0)
        y = Coords(1, 1, 1)
        self.assertAlmostEqual(math.sqrt(3), x.distance_to(y))
