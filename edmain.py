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

from edpath import Distance, MultiDistance


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
    # mypath = MultiDistance(Distance(config.WP8TO9TXT))
    # mypath = MultiDistance(Distance(config.WP7TO8TXT),
    #                        Distance(config.WP8TO9TXT))
    # mypath = MultiDistance(config.WP7TO8TXT, config.WP8TO9TXT)

    # with open('WP7TO8.txt') as f:
        # mypath = Distance(string.join(f.readlines()))
        # mypath = Distance(mypath.path[2:9])
    mypath = Distance(string.join(fileinput.input()))
    # mypath.shuffle_poi()
    # mypath = Distance(config.WP8TO9TXT)

    print('Direct path is %.2f ly' % mypath.direct_length)

    mypath.print_path(mypath.best_path_with_split()[-1])
    # print(mypath.best_path())
    # mypath.print_path(mypath.best_path()[-1])

    # stat is wrong because we call best_path three times and with three different lists
    # mypath.print_stats()
