"""main code"""
from __future__ import print_function, unicode_literals

import math

import config
from edpath import Distance


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
    mypath = Distance(path)
    print('Direct path is %.2f ly' % mypath.direct_length)

    best_len, best_path = mypath.best_path()

    print('-' * 60)
    print(best_len)
    print(best_path)

    for n, curr in enumerate(best_path):
        if n < len(best_path) - 1:
            to_last = Distance(best_path[n:])
            print('  ' * n,
                  curr.alias,
                  ' > %.2f ly to next' % curr.distance_to(best_path[n + 1]),
                  ' >> %.2f ly to last by poi' % to_last.len_path_asis,
                  ' >>> %.2f ly to last directly' % to_last.direct_length,
                 )
        else:
            print('  ' * n, curr.alias)

    print('Paths considered: %d, paths rejected early %d' % (mypath.pcount, mypath.rcount))
    fv, fr = mypath.fact
    print('Total %d! combinations' % fv)
    print('Paths not even considered: %d' % (fr - mypath.rcount - mypath.pcount))

if __name__ == '__main__':
    run_main(config.WP7TO8)

"""
12025.0323703
 Crown Of Ice  > 104.23 ly to next  >> 12025.03 ly to last by poi  >>> 5556.59 ly to last directly
   Silver Highway  > 841.81 ly to next  >> 11920.80 ly to last by poi  >>> 5486.01 ly to last directly
     _ G2 Dust Cloud  > 987.63 ly to next  >> 11078.99 ly to last by poi  >>> 5799.48 ly to last directly
       _ Karkina Nebula  > 1959.40 ly to next  >> 10091.36 ly to last by poi  >>> 6277.50 ly to last directly
         _ Stairway To Heaven  > 1577.14 ly to next  >> 8131.97 ly to last by poi  >>> 4343.28 ly to last directly
           Dark Eye Nebula  > 2175.84 ly to next  >> 6554.83 ly to last by poi  >>> 5201.85 ly to last directly
             Braisio Juliet Nebula Cluster  > 916.33 ly to next  >> 4378.99 ly to last by poi  >>> 3450.68 ly to last directly
               _ Lyaisae Juliet Nebula Cluster  > 488.12 ly to next  >> 3462.67 ly to last by poi  >>> 3055.05 ly to last directly
                 _ Black Giants Nebula  > 1678.87 ly to next  >> 2974.55 ly to last by poi  >>> 2901.13 ly to last directly
                   Breakthrough Echoes  > 1295.67 ly to next  >> 1295.67 ly to last by poi  >>> 1295.67 ly to last directly
                     Goliath's Rest  > 0.00 ly to next  >> 0.00 ly to last by poi  >>> 0.00 ly to last directly
Paths considered: 18, paths rejected early 362862
Paths not even considered: 39553920
python edmain.py  7.92s user 0.07s system 99% cpu 8.001 total
"""
