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

    mypath.print_stats()

if __name__ == '__main__':
    run_main(config.WP7TO8[9:])
