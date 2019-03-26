#!/bin/sh

i=2
CFG=WP7TO8.txt

find .edpathcache -type f | xargs grep -l found_len | xargs rm
cat $CFG | python edmain.py > 1

while ((i>0)); do
    echo $i
    find .edpathcache -type f | xargs grep -l found_len | xargs rm
    cat $CFG | time python edmain.py | diff 1 -
    if [[ $? -ne 0 ]]; then
        i=0
    fi
    ((i--))
done

# test with shuffle and cache removal
# Time      Cached  Caching Distance    Files in cache
# 2:14.08   -       4       33287.00    5807    # even better
