# -*- coding: utf-8 -*-
"""Font unit arrangements from Monotype information booklets
(found at Alembic Press)"""
# Define unit arrangements for the fonts
# This may in future be stored in data files (JSON-encoded?)
UA = {'0': dict(r={}, b={}, i={}, s={}, l={}, u={}),
      '82': dict(r={5: [*'fiIjJl'], 7: [*'st'], 8: [*'acrz'],
                    9: [*'eFgSvy1234567890'],
                    10: [*'bdEhkLnopPqux', 'ff', 'fi', 'fl'],
                    11: [*'BT'], 12: [*'RVY', 'ae'], 13: [*'ACKZ&'],
                    14: [*'DGHUwX'], 15: [*'MmNOQ', 'oe', 'ffi', 'ffl'],
                    17: ['AE', 'OE'], 20: ['W']}),
      '93': dict(r={6: [*'fijl'], 7: [*'IJ'], 8: [*'st'],
                    9: [*'cr1234567890'], 10: [*'aegvyz', 'fl'],
                    11: [*'bdFhknopqSux', 'fi'], 12: [*'ELP', 'ff'],
                    13: [*'BRT'], 14: [*'CKVYZ&', 'ae'], 15: [*'ADGw'],
                    16: [*'HNOQUX', 'oe'], 17: ['M', 'ffi', 'ffl'],
                    18: [*'mW', 'OE'], 20: ['AE', 'OE'], 22: ['W']}),
      '311': dict(i={5: [*'IiJjl'], 6: [*'ft'], 7: [*'rs'], 8: [*'ceFLoSvy'],
                     9: [*'abdghknPpquxz123456789', 'fi', 'fl'],
                     10: [*'ABERTVY'], 11: [*'CK', 'ff'],
                     12: [*'DGOQUwZ&', 'ae'], 13: [*'HNX', 'oe'],
                     14: ['m', 'ffi', 'ffl'], 15: ['M'], 16: ['AE'],
                     18: ['W', 'OE']}),
      '324': dict(r={5: [*'ijl'], 6: [*'ft'], 7: [*'Irs'], 8: [*'cevz'],
                     9: [*'abdghnopquy1234567890'], 10: [*'Jkx', 'fi', 'fl'],
                     11: [*'FS', 'ae', 'oe', 'ff'], 12: [*'BELPTw&'],
                     13: [*'ACKRVXYZ'], 14: [*'DGmNU'],
                     15: [*'HOQ', 'ffi', 'ffl'], 18: [*'MW', 'AE', 'OE']}),
      '325': dict(r={5: [*'ijl'], 6: [*'ft'], 7: [*'Irs'], 8: [*'ceJz'],
                     9: [*'agvxy1234567890'], 10: [*'bdhknopqSu', 'fi', 'fl'],
                     11: ['P', 'ff'], 12: [*'BEFLTZ', 'ae'],
                     13: [*'CVw', 'oe'], 14: [*'AOQRXY&'],
                     15: [*'DGHKmNU', 'ffi', 'ffl'], 18: [*'MW', 'AE', 'OE']},
                  i={5: [*'ijl'], 6: [*'ft'], 7: [*'Irs'], 8: [*'cevz'],
                     9: [*'abdghJnopquy1234567890'], 10: [*'kx', 'fi', 'fl'],
                     11: [*'FS', 'ae', 'oe', 'ff'], 12: [*'BELPTw'],
                     13: [*'ACGKRVXYZ&'], 14: [*'DmNOQU'],
                     15: ['H', 'ffi', 'ffl'], 18: [*'MW', 'AE', 'OE']},
                  s={5: ['i'], 6: ['j'], 7: ['s'], 8: [*'ef'], 9: [*'blpt'],
                     10: [*'acoqrvxyz'], 11: [*'dghknu'], 12: ['m'],
                     13: ['ae'], 14: ['oe'], 15: ['w']})}
