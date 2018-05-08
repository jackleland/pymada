import numpy as np

# Index hull zones as clockwise from front
# Hull zone lines are similarly indexed as each hull zone's left most line when looking from the centre out.
FRONT_ARC = 0
LEFT_ARC = 3
RIGHT_ARC = 1
REAR_ARC = 2

# DIAGRAM:
# L1________L2
#  |\      /|  ^ Front
#  | \ Z1 / |
#  |  \  /  |
#  |Z4 \/ Z2|
#  |   /\   |
#  |  /  \  |
#  | / Z3 \ |
#  |/______\|  v Rear
# L4        L3
#

# movement ruler constants in mm
RULER_WIDTH = 3.0
RULER_LENGTH_1 = 30.0
RULER_LENGTH_2 = 15.0


class HullZones(list):
    def __init__(self, front_val, left_val, right_val, rear_val):
        super().__init__([front_val, right_val, rear_val, left_val])


class ShieldHullZones(HullZones):
    def is_shielded(self, hull_zone):
        return self[hull_zone] > 0

    def take_damage(self, hull_zone, damage=1):
        assert 0 <= hull_zone < len(self)
        if self[hull_zone] >= damage:
            self[hull_zone] -= damage
            return 0
        else:
            carry_over = damage - self[hull_zone]
            self[hull_zone] = 0
            return carry_over


class FiringHullZones(HullZones):
    def __init__(self, front_pool, left_pool, right_pool, rear_pool, front_angle, rear_angle, apex_dist, los_points=None):
        assert len(front_pool) == 3 and len(left_pool) == 3 and len(right_pool) == 3 and len(rear_pool) == 3
        super().__init__(front_pool, left_pool, right_pool, rear_pool)
        self.front_angle = front_angle
        self.rear_angle = rear_angle
        self.apex_dist = apex_dist
        if los_points and isinstance(los_points, list):
            self.los_points = HullZones(*los_points)
        elif isinstance(los_points, HullZones) or not los_points:
            self.los_points = los_points

    def get_range_pool(self, hull_zone, dice_range):
        assert dice_range in [1, 2, 3]
        return self[hull_zone][:dice_range]


class Ship(object):

    def __init__(self, ship_definition, x_pos, y_pos, angle, speed, upgrades=None, defence_tokens=None, docked=None,
                 command_tokens=None, shields=None, hull_damage=0, damage_effects=None, special_points=None):
        assert isinstance(ship_definition, ShipDefinition)
        self.ship_definition = ship_definition
        self.pos = np.matrix([[x_pos], [y_pos]])
        self.vector = self.rotation_mat(angle) * np.matrix([[1], [0]])
        self.speed = speed
        self.upgrades = upgrades
        self.defence_tokens = defence_tokens
        self.command_tokens = command_tokens
        if shields:
            self.shields = shields
        else:
            self.shields = ShieldHullZones(*ship_definition.shields)
        self.hull_damage = hull_damage
        self.damage_effects = damage_effects
        self.docked = docked
        self.special_points = special_points

    def get_points(self):
        return self.ship_definition.point_cost + self.special_points + self.upgrades.get_points()

    def has_line_of_sight(self, origin, hull_zone):
        destination_on_ship = self.ship_definition.arcs.los_points[hull_zone]

    def rotation_mat(self, angle):
        theta = np.radians(angle)
        return np.matrix([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

    def move(self, movement, is_navigate=False, is_engine_techs=False):
        if is_engine_techs and (len(movement) != 1 or -2 <= movement[0] <= 2):
            raise ValueError('Invalid engine techs movement given')
        if not self.ship_definition.is_move_legal(movement, is_navigate=is_navigate):
            raise ValueError('Move given ({}) not legal for ship definition {}'
                             .format(movement, self.ship_definition.name))
        # Decide which side of ruler to use
        # TODO: This assumption may not be strictly true for larger ships, may need a rethink later in development
        ruler_side = 1
        for yaw in reversed(movement):
            if yaw == 0:
                continue
            else:
                ruler_side = np.sign(yaw)
                break
        # Move
        w = ruler_side * np.matrix([[0.0], [RULER_WIDTH]])
        l_1 = np.matrix([[RULER_LENGTH_1], [0.0]])
        l_2 = np.matrix([[RULER_LENGTH_2], [0.0]])
        movement_vector = self.pos + w
        rotations = []
        total_angle = 0
        for i, yaw in enumerate(movement):
            angle = 22.5 * yaw
            total_angle += angle
            R = self.rotation_mat(angle)
            rotations.append(R)
            term = l_1 + (R * l_2)
            for j in reversed(range(i)):
                term = rotations[j] * term
            movement_vector += term
        w_end = w
        for R in reversed(rotations):
            w_end = R * w_end
        movement_vector = self.rotation_mat(total_angle) * (movement_vector + w_end)

        new_pos = self.pos + movement_vector
        new_vector = self.rotation_mat(total_angle) * self.vector
        return new_pos, new_vector


class ShipDefinition(object):

    def __init__(self, ship_class, name, faction, size, command_value, squadron_value, engineering_value, defence_tokens, hull,
                 shields, arcs, yaw_values, anti_squadron, point_cost, upgrade_slots):
        """

        :param type:
        :param name:
        :param size:
        :param command_value:
        :param squadron_value:
        :param engineering_value:
        :param defence_tokens:
        :param hull:
        :param shields:
        :param arcs:
        :param yaw_values:           list of max_yaw indexed by speed. len(movements) gives maximum speed.
                                    e.g. [ [2], [1, 2], [1, 1, 2], [0, 1, 1, 2] ]
        :param anti_squadron:
        :param point_cost:
        :param upgrade_slots:
        """
        self.ship_class = ship_class
        self.name = name
        self.faction = faction
        self.size = size

        self.command_value = command_value
        self.squadron_value = squadron_value
        self.engineering_value = engineering_value

        self.defence_tokens = defence_tokens
        self.hull = hull
        self.shields = shields
        self.arcs = arcs
        self.anti_squadron = anti_squadron
        self.yaw_values = yaw_values

        self.point_cost = point_cost
        self.upgrade_slots = upgrade_slots

    def is_move_legal(self, movement, is_navigate=False):
        navigates_used = 0
        movement_speed = len(movement) - 1
        if movement_speed <= len(self.yaw_values):
            for speed in range(movement_speed):
                yaw = abs(movement[speed])
                max_yaw = self.yaw_values[movement_speed][speed]
                if is_navigate and max_yaw < 2:
                    max_yaw += 1
                if yaw > max_yaw:
                    print('That is not a legal move, yaw value at speed node {} is '.format(speed) +
                          'above maximum yaw value for that speed')
                    return False
                if yaw == max_yaw and is_navigate:
                    is_navigate = False
                    navigates_used += 1
                    print('Navigate used at speed {}'.format(speed))
            return True
        else:
            print('Not a legal move, movement speed exceeds maximum allowed speed for ship {}'.format(self.name))
            return False


class Squadron(object):
    def __init__(self, squadron_definition, engaged=0, activated=False, defence_tokens=None, hull_damage=None):
        self.squadron_definition = squadron_definition
        self.engaged = engaged
        self.activated = activated
        self.defence_tokens = defence_tokens
        self.hull_damage = hull_damage


class SquadronDefinition(object):
    def __init__(self, name, type, hull, speed, anti_squadron, anti_ship, defence_tokens, abilities, point_cost,
                 unique=False):
        self.name = name
        self.type = type
        self.hull = hull
        self.speed = speed
        self.anti_squadron = anti_squadron
        self.anti_ship = anti_ship
        self.defence_tokens = defence_tokens
        self.abilities = abilities
        self.point_cost = point_cost
        self.unique = unique


class Board(object):
    def __init__(self, size, ships, obstacles, squadrons):
        self.size = size
        self.ships = ships
        self.obstacles = obstacles
        self.squadrons = squadrons
