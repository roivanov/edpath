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
# 2:23.76   -       4       34935.56    
# 2:17.08   4       -       37505.50    6089
# 2:13.47   -       4       34935.56    6089
# 2:27.94   4       -       38132.82    6089
# 2:23.59   4       -       36697.20    6089
# 2:36.15   4       -       34304.50    6089
# 2:11.48   4       -       33680.28    6089    # randomization disabled
# 2:12.80   4       -       -//-        -//-    # consistent with randomization disabled
# 2:14.08   -       4       33287.00    5807    # even better
