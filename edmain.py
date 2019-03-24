"""
main code

TODO prespawn and keep threads running
TODO remove duplicated in systems (this disables returning to poi)
TODO cache poi computed best path: sort poi, create checksum, save best path
"""

from __future__ import print_function, unicode_literals

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
    # mypath = Distance(config.WP7TO8TXT + config.WP8TO9TXT)
    mypath = Distance(config.WP8TO9TXT)
    print('Direct path is %.2f ly' % mypath.direct_length)

    mypath.print_path(mypath.best_path_with_split()[-1])

    # stat is wrong because we call best_path three times and with three different lists
    # mypath.print_stats()
