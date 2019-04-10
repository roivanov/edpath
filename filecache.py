from __future__ import print_function

import datetime
import hashlib
import os
from contextlib import contextmanager


class NoCache(object):
    def __init__(self, cache_name):
        self._cache_name = cache_name
        self._key = None

    def save(self, data):
        pass

    def read(self):
        return None

    @staticmethod
    def print_cache_hit_histogram():
        pass


class MemCache(NoCache):
    cache = {}
    hit = {}
    miss = {}
    time_spent = {}
    reads = 0
    hits = 0
    misses = 0

    def __init__(self, cache_name):
        super(MemCache, self).__init__(cache_name)
        if self._cache_name:
            self._key = self.gen_hash(self._cache_name)

            if self._key not in MemCache.cache:
                MemCache.cache[self._key] = None
                MemCache.hit[self._key] = 0
                MemCache.miss[self._key] = 0
                MemCache.time_spent[self._key] = 0

    @staticmethod
    def gen_hash(s):
        return hashlib.sha256(s).hexdigest()

    def save(self, data, time_spent=None):
        if self._key:
            if MemCache.cache.get(self._key, None):
                raise ValueError('Duplicate value %s for key %s' % (self._cache_name, self._key))
            else:
                MemCache.cache[self._key] = data
            if time_spent:
                MemCache.time_spent[self._key] = time_spent

    def read(self):
        ret = None

        if self._key:
            MemCache.reads += 1
            ret = MemCache.cache.get(self._key, None)
            if ret:
                MemCache.hits += 1
                MemCache.hit[self._key] += 1
            else:
                MemCache.misses += 1
                MemCache.miss[self._key] += 1

        return ret

    def remove(self):
        raise NotImplementedError

    @staticmethod
    def print_cache_hit_histogram():
        if len(MemCache.cache) > 0:
            print('cache: size=%4d' % len(MemCache.cache))
        else:
            print('Nothing got in cache')
            return

        systems = len(MemCache.hit)
        hit_count = max(MemCache.hit.values())
        print('hit:   size=%4d, max=%4d, total=%d' % (len(MemCache.hit),
                                                      hit_count, MemCache.hits))
        miss_count = max(MemCache.miss.values())
        print('miss:  size=%4d, max=%4d, total=%d' % (len(MemCache.miss),
                                                      miss_count, MemCache.misses))

        step = max(hit_count / 10, 1)
        start = 0
        finish = 0
        total_time_saved = 0
        print('         hits       ')
        print('      min -   max: path variants (time saved)')
        while start < hit_count:
            hits_in_range = {k: v for k, v in MemCache.hit.items()
                             if start <= v <= finish}
            range_hit_count = len(hits_in_range)

            time_saved = sum([MemCache.time_spent[k] * hits_in_range[k]
                              for k in hits_in_range])
            try:
                time_saved_str = str(datetime.timedelta(seconds=time_saved)).split('.')[0]
            except OverflowError:
                time_saved_str = 'oo'
            total_time_saved += time_saved

            if range_hit_count == 0:
                range_hit_count_str = '.'
            else:
                range_hit_count_str = '.' * (2 + 30 * range_hit_count / systems)
            print('    %5d - %5d: %5d %s (%s)' % (start,
                                                  min(finish, hit_count),
                                                  range_hit_count,
                                                  range_hit_count_str,
                                                  time_saved_str))
            if start == 0:
                start = 1
            else:
                start += step
            finish += step

        print('mem cache reads %d, hit ratio %.1f' % (MemCache.reads,
                                                      (100.0 * MemCache.hits / MemCache.reads)))
        try:
            total_time_saved_str = str(datetime.timedelta(seconds=total_time_saved)).split('.')[0]
        except OverflowError:
            total_time_saved_str = 'oo'
        print('time saved %s' % total_time_saved_str)


class FileCache(MemCache):
    """File Cache of the objects or data"""

    # cache directory
    CACHE_DIR = '.edpathcache'
    # number of chracters used to build cache tree
    _DIR_CHAR = 2

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    def __init__(self, cache_name):
        super(FileCache, self).__init__(cache_name=cache_name)
        if cache_name:
            self.__fname = FileCache.set_fname(cache_name)
        else:
            self.__fname = None

    @staticmethod
    def set_fname(utf8_encoded_name):
        if utf8_encoded_name:
            _hash = MemCache.gen_hash(utf8_encoded_name)
            base_dir = os.path.join(FileCache.CACHE_DIR, _hash[:FileCache._DIR_CHAR])
            if not os.path.exists(base_dir):
                os.mkdir(base_dir)

            return os.path.join(base_dir, _hash[FileCache._DIR_CHAR:])
        else:
            return None

    @property
    def fname(self):
        return self.__fname

    @fname.setter
    def fname(self, value):
        self.__fname = FileCache.set_fname(value)

    def save(self, data):
        if self.fname:
            with open(self.fname, 'w') as f:
                f.write(data)

        # else:
            # print('WARNING data was not saved because fname is Not set')

    @contextmanager
    def open(self):
        if self.fname and os.path.exists(self.fname):
            # print('Loading from file')
            with open(self.fname) as f:
                yield f
        else:
            yield None

    def remove(self):
        os.remove(self.fname)
