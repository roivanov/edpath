# edpath
Elite Dangerous: Distant Worlds #2 route planner

Save DW2 path into any file and pass it to commant `python edmain.py < file.txt`

Example input:
```Cerulean Tranquility - GalMap Ref: Phroi Bluae QI-T e3-3454

# To see on the way;
The Zinnia Haze - GalMap Ref: Hypuae Briae LC-U e3-152
Hydrangea Nebula - GalMap Ref: Hyuqeae MT-Q e5-4335
Magnus Nebula - GalMap Ref: Hypuae Briae YQ-Z c28-339
Neighbouring Necklaces - GalMap Ref: Vegnoae BK-R d4-1105

# Minor POI's (off-route);
Undine Haven - GalMap Ref: Phroi Bluae LS-B d13-744_
The Briar Patch Nebula - GalMap Ref: Hypuae Briae BV-Y e3851_
Infinite Bonds - GalMap Ref: Hypuae Briae YF-E d12-2760_
Eos Nebula - GalMap Ref: Vegnoae WE-R e4-9257_

# Arrive at:
Morphenniel Nebula - GalMap Ref: Bleethuae NI-B D674
```

Example output:
```
|  ----------------------- | ----------- | ----------- | ----------- |
|            Name          |     Next    |     Path    |     Last    |
|  ----------------------- | ----------- | ----------- | ----------- |
|    Cerulean Tranquility  |   553.14 ly |  9587.25 ly |  3227.23 ly |
|       _Undine Haven      |  1861.29 ly |  9034.10 ly |  2753.83 ly |
|  _The Briar Patch Nebula |  1023.48 ly |  7172.82 ly |  2702.58 ly |
|      The Zinnia Haze     |  1374.11 ly |  6149.33 ly |  2787.62 ly |
|      Hydrangea Nebula    |   841.39 ly |  4775.22 ly |  2241.14 ly |
|       Magnus Nebula      |   354.73 ly |  3933.83 ly |  2029.34 ly |
|      _Infinite Bonds     |  1576.21 ly |  3579.10 ly |  2103.11 ly |
|   Neighbouring Necklaces |   636.42 ly |  2002.90 ly |  1265.68 ly |
|        _Eos Nebula       |  1366.48 ly |  1366.48 ly |  1366.48 ly |
|     Morphenniel Nebula   |      -      |      -      |      -      |
|  ----------------------- | ----------- | ----------- | ----------- |
```

Note underscore `_` character in some systems: this marks minor POI if you like to skip them.
