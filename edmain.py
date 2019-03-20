"""main code"""
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

def run_main(path):
    # direct path from A to Z
    mypath = Distance(path)
    print('Direct path is %.2f ly' % mypath.direct_length)

    mypath.print_path(*mypath.best_path())

    mypath.print_stats()

if __name__ == '__main__':
    run_main(config.WP7TO8[9:])
