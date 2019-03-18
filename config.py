# pylint: disable=missing-docstring

from edsystems import System, Coords

WP6TO7 = [System('Great Annihilator'),

          System('Zunuae HL-Y e6903', 'Zunuae Nebula'),
          System('Hypoe Flyi HW-W e1-7966', 'Galionas'),
          System('HYPOE FLYI HX-T E3-295', 'Caeruleum Luna "Mysturji Crater"'),
          System('Byoomao MI-S e4-5423', 'Wulfric'),
          System('Sagittarius A*'),

          # visiting this system adds another 3k ly to the distance
          System('Kyli Flyuae WO-A f39', '*** Dance of the Compact Quartet'),
          System('Myriesly DQ-G d10-1240', 'Insinnergy\'s World'),
          System('Myriesly RY-S e3-5414', 'Six Rings'),
          System('Myriesly CL-P e5-4186', 'Emerald Remnant'),
          System('Myriesly CL-P e5-7383', 'Fenrisulfur'),

          System('STUEMEAE KM-W C1-342', 'WP7 Altum Sagittarii'),
         ]

WP6TO7H2 = [#System('PHRAA FLYUAE EB-C C27-1592'),
            System('Kyli Flyuae WO-A f39', '*** Dance of the Compact Quartet'),

            System('Byoomao MI-S e4-5423', 'Wulfric'),
            System('Sagittarius A*'),

            System('Myriesly DQ-G d10-1240', 'Insinnergy\'s World'),
            System('Myriesly RY-S e3-5414', 'Six Rings'),
            System('Myriesly CL-P e5-4186', 'Emerald Remnant'),
            System('Myriesly CL-P e5-7383', 'Fenrisulfur'),

            System('STUEMEAE KM-W C1-342', 'WP7 Altum Sagittarii'),
           ]

WP7TO8 = [#System('Sagittarius A*'),
          # Major POI
          #1
          #System('Phua Aub VY-S e3-3899', 'Phua Aub Archer Beta'),
          #System('Phua Aub MX-U e2-7396', 'Phua Aub Archer Epsilon'),
          #System('Phua Aub SJ-R e4-8234', 'Phua Aub Archer Kappa'),
          #2
          System('Phipoea WK-E d12-1374', '1 Crown Of Ice'),
          System('Phipoea HJ-D c27-5254', '2 Silver Highway'),
          #3
          System('Rothaei SI-B e2047', '3 Dark Eye Nebula'),
          #4&5
          System('Braisio FR-V e2-293', '4 Braisio Juliet Nebula Cluster'),
          System('Rhuedgie KN-T e3-721', '5 Breakthrough Echoes'),

          #Minor POI
          #System('Juenae OX-U e2-8852', '_ Hengist Nebula'),
          #System('GRS 1739-278', '_ GRS 1739-278'),
          System('Eok Bluae GX-K d8-1521', '_ Karkina Nebula'),
          System('G2 Dust Cloud Sector JH-V c2-2851', '_ G2 Dust Cloud'),
          System('Dryau Chrea DB-F d11-3866', '_ Stairway To Heaven'),
          System('Eorl Broae EB-O e6-1507', '_ Black Giants Nebula'),
          System('Lyaisae HA-A e3363', '_ Lyaisae Juliet Nebula Cluster'),

          # FINISH at
          System('Swoals IL-Y e0', 'Goliath\'s Rest')
]

TEST = [System('A', coords=Coords(0, 0, 0)),
        System('Z', coords=Coords(1000, 1000, 1000))
]
