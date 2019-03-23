"""main code"""
from __future__ import print_function, unicode_literals

import copy

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

if __name__ == '__main__':
    # direct path from A to Z
    mypath = Distance(config.WP7TO8)
    print('Direct path is %.2f ly' % mypath.direct_length)

    mypath.print_path(mypath.best_path_with_split()[-1])

    # stat is wrong because we call best_path three times and with three different lists
    # mypath.print_stats()
