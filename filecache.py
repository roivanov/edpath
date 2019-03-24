from __future__ import print_function

import hashlib
import os
from contextlib import contextmanager


class FileCache(object):
    """File Cache of the objects or data"""

    # cache directory
    CACHE_DIR = '.edpathcache'
    # number of chracters used to build cache tree
    _DIR_CHAR = 2

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    def __init__(self, utf8_encoded_name):
        self.__fname = FileCache.set_fname(utf8_encoded_name)
        print(self.__fname)
        raise NotImplementedError

    @staticmethod
    def set_fname(utf8_encoded_name):
        if utf8_encoded_name:
            _hash = hashlib.sha256(utf8_encoded_name).hexdigest()
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
