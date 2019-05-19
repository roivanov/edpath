"""
main code

TODO Distance: prespawn and keep threads running
TODO FileCahce: cache with class name
TODO MultiDistane: threads in multipath
TODO Distance: tune path length to cache
TODO Distance: print distance name
"""

from __future__ import print_function, unicode_literals

import fileinput
import string

from src.edpath import Distance


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
    mypath = Distance(string.join(fileinput.input()))

    print('Direct path is %.2f ly' % mypath.direct_length)

    mypath.print_path(mypath.best_path()[-1])

    mypath.print_cache_hit_histogram()
