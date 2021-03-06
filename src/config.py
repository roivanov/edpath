# -*- coding: utf-8 -*-
# # pylint: disable=missing-docstring

from src.edsystems import System, Coords, mSystem

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

WP7TO8 = [System('Sagittarius A*'),
          # Major POI
          #1/1,2,3
          System('Phua Aub VY-S e3-3899', 'Phua Aub Archer Beta'),
          System('Phua Aub MX-U e2-7396', 'Phua Aub Archer Epsilon'),
          System('Phua Aub SJ-R e4-8234', 'Phua Aub Archer Kappa'),

          mSystem('GRS 1739-278', 'GRS 1739-278'),
          mSystem('Juenae OX-U e2-8852', 'Hengist Nebula'),
          mSystem('G2 Dust Cloud Sector JH-V c2-2851', 'G2 Dust Cloud'),
          #2
          System('Phipoea WK-E d12-1374', 'Crown Of Ice'),
          System('Phipoea HJ-D c27-5254', 'Silver Highway'),
          mSystem('Eok Bluae GX-K d8-1521', 'Karkina Nebula'),
          #3
          System('Rothaei SI-B e2047', 'Dark Eye Nebula'),
          #4&5
          System('Braisio FR-V e2-293', 'Braisio Juliet Nebula Cluster'),
          System('Rhuedgie KN-T e3-721', 'Breakthrough Echoes'),

          #Minor POI
          mSystem('Dryau Chrea DB-F d11-3866', 'Stairway To Heaven'),
          mSystem('Eorl Broae EB-O e6-1507', 'Black Giants Nebula'),
          mSystem('Lyaisae HA-A e3363', 'Lyaisae Juliet Nebula Cluster'),

          mSystem('Hypiae Phyloi LR-C D22'),
          # FINISH at
          System('Swoals IL-Y e0', 'Goliath\'s Rest')
]

TEST = [System('A', coords=Coords(0, 0, 0)),
        System('B', coords=Coords(100, 0, 0)),
        System('C', coords=Coords(150, 0, 0)),
        System('Y', coords=Coords(950, 0, 0)),
        System('D', coords=Coords(200, 0, 0)),
        System('Z', coords=Coords(1000, 0, 0))
]
