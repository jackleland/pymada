from main import Ship, ShipDefinition, FiringHullZones

# Defense tokens
DEFTKN_EVADE = 'evade'
DEFTKN_BRACE = 'brace'
DEFTKN_REDIRECT = 'redirect'
DEFTKN_CONTAIN = 'contain'
DEFTKN_SCATTER = 'scatter'

# base sizes in mm
sizes = [[41, 71], [61, 102], [76, 129]]

def_cr90a = ShipDefinition('CR90', 'CR90a', 'rebel', 0,
                           1, 1, 2,
                           [DEFTKN_EVADE, DEFTKN_EVADE, DEFTKN_REDIRECT],
                           4,
                           [2, 2, 1, 2],
                           FiringHullZones([0, 1, 2], [0, 1, 1], [0, 1, 1], [0, 0, 1], 45, 45, 25),
                           [[2], [1, 2], [0, 1, 2], [0, 1, 1, 2]],
                           [0, 1, 0],
                           44, None)

if __name__ == '__main__':
    corvette = Ship(def_cr90a, 10, 10, 0.1, 3)
    corvette.move([0, -1, 2])