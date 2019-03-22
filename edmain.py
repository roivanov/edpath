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

    scaled = mypath.scale()
    middle = len(scaled) / 2

    finish = mypath.finish
    best_l = 0
    best_best = None
    for n in range(-1, 2):
        mypath.path = [mypath.start] + scaled[:middle + n +1]
        path_one = mypath.best_path(skip_minor=False)[-1]
        mypath.path = scaled[middle + n:] + [finish]
        path_two = mypath.best_path(skip_minor=False)[-1]
        assert path_one[-1] == path_two[0]

        mypath.path = path_one + path_two[1:]
        l = mypath.len_path_asis
        if best_l == 0 or l < best_l:
            best_l = l
            best_best = copy.copy(mypath.path)
            print(n, l, path_two[0].alias, len(path_one), len(path_two))

    mypath.print_path(best_best)

    # stat is wrong because we call best_path three times and with three different lists
    # mypath.print_stats()
