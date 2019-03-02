"""
Find shortest path between two systems while visiting all POI in between
"""
from __future__ import print_function, unicode_literals

import random

from edsystems import System


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
        # all permutations of poi systems
        i = self.emit(poi or [])
        for each in i:
            try:
                curr_len = self.length(list(each), limit=_best_len)
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
            if not self.deep:
                random.shuffle(poi)

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

def wrap_to_profile(func):
    def _wrap(*args, **kwargs):
        import cProfile, pstats, StringIO
        pr = cProfile.Profile()
        pr.enable()
        ret = func(*args, **kwargs)
        pr.disable()
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        return ret
    return _wrap

SYSTEMS = [System('Great Annihilator'),

           System('Zunuae HL-Y e6903', 'Zunuae Nebula'),
           System('Hypoe Flyi HW-W e1-7966', 'Galionas'),
           System('HYPOE FLYI HX-T E3-295', 'Caeruleum Luna "Mysturji Crater"'),
           System('Byoomao MI-S e4-5423', 'Wulfric'),
           System('Sagittarius A*'),

           # visiting this system adds another 3k ly to the distance
           System('Kyli Flyuae WO-A f39', '*** Dance of the Compact Quartet'),
           System('Myriesly DQ-G d10-1240', 'Insinnergy\'s World'),
           System('Myriesly RY-S e3-5414', 'Six Rings'),
           System('Myriesly CL-P e5-4186', 'Emerald Remnant'),
           System('Myriesly CL-P e5-7383', 'Fenrisulfur'),

           System('STUEMEAE KM-W C1-342', 'WP7 Altum Sagittarii'),
          ]

def run_main(path):
    # direct path from A to Z
    mypath = PathTo(path[0], path[-1])
    print('Direct path is %.2f ly' % mypath.length(poi=None))

    best_len, best_order = wrap_to_profile(mypath.best_path)(poi=path[1:-1])

    print('-' * 60)
    print(best_len)
    best_path = path[:1] + best_order + path[-2:]

    i = iter(best_path)
    curr = None
    nxt = i.next()
    n = 0
    while nxt:
        try:
            curr = nxt
            nxt = i.next()
        except StopIteration:
            nxt = None

        to_last = PathTo(curr, best_path[-1])
        print('  ' * n,
              curr.alias,
              ' > %.2f ly to next' % curr.distance_to(nxt or curr),
              ' >> %.2f ly to last by poi' % to_last.length(poi=best_path[n+1:-1]),
              ' >>> %.2f ly to last directly' % to_last.length(poi=[]),
              )
        n += 1

    print(mypath.pcount)

if __name__ == '__main__':
    run_main(SYSTEMS)


# 10487.3914861 ly

# 229523138 function calls (190628638 primitive calls) in 133.731 seconds
# 221822632 function calls (182928132 primitive calls) in 114.752 seconds
# with store len
# 139839636 function calls (100945136 primitive calls) in 84.637 seconds
# with store len both ways
# 139839459 function calls (100944959 primitive calls) in 85.496 seconds
# 426782242 function calls (387887742 primitive calls) in 198.585 seconds
