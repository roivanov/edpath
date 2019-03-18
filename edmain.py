"""main code"""
from __future__ import print_function, unicode_literals

import math

import config
from edpath import PathTo

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

def run_main(path):
    # direct path from A to Z
    mypath = PathTo(path[0], path[-1])
    print('Direct path is %.2f ly' % mypath.length(poi=None))

    best_len, best_order = wrap_to_profile(mypath.best_path)(poi=path[1:-1])

    print('-' * 60)
    print(best_len)
    best_path = path[:1] + best_order + path[-1:]

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

    print('Paths considered: %d, paths rejected early %d' % (mypath.pcount, mypath.rcount))
    print('Paths not even considered: %d' % (math.factorial(len(path)) - mypath.rcount - mypath.pcount))

if __name__ == '__main__':
    run_main(config.WP7TO8)


# 10487.3914861 ly

# 229523138 function calls (190628638 primitive calls) in 133.731 seconds
# 221822632 function calls (182928132 primitive calls) in 114.752 seconds
# with store len
# 139839636 function calls (100945136 primitive calls) in 84.637 seconds
# with store len both ways
# 139839459 function calls (100944959 primitive calls) in 85.496 seconds
# 426782242 function calls (387887742 primitive calls) in 198.585 seconds
