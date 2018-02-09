
FRONT_ARC = 'front'
LEFT_ARC = 'left'
RIGHT_ARC = 'right'
REAR_ARC = 'rear'


class HullZones(dict):
    def __init__(self, front_val, left_val, right_val, rear_val):
        super().__init__()
        self[FRONT_ARC] = front_val
        self[LEFT_ARC] = left_val
        self[RIGHT_ARC] = right_val
        self[REAR_ARC] = rear_val


class ShieldHullZones(HullZones):
    def is_shielded(self, hull_zone):
        return self[hull_zone] > 0

    def take_damage(self, hull_zone, damage=1):
        assert hull_zone in self
        if self[hull_zone] >= damage:
            self[hull_zone] -= damage
            return 0
        else:
            carry_over = damage - self[hull_zone]
            self[hull_zone] = 0
            return carry_over


class FiringHullZones(HullZones):
    def __init__(self, front_pool, left_pool, right_pool, rear_pool, front_angle, rear_angle):
        assert len(front_pool) == 3 and len(left_pool) == 3 and len(right_pool) == 3 and len(rear_pool) == 3
        super().__init__(front_pool, left_pool, right_pool, rear_pool)
        self.front_angle = front_angle
        self.rear_angle = rear_angle

    def get_range_pool(self, hull_zone, dice_range):
        assert dice_range in [1, 2, 3]
        return self[hull_zone][:dice_range]


class Ship(object):

    def __init__(self, ship_definition, x_pos, y_pos, angle, speed, upgrades=None, defence_tokens=None, docked=None,
                 command_tokens=None, shields=None, hull_damage=0, damage_effects=None, special_points=None):
        self.ship_definition = ship_definition
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.angle = angle
        self.speed = speed
        self.upgrades = upgrades
        self.defence_tokens = defence_tokens
        self.command_tokens = command_tokens
        if shields:
            self.shields = shields
        else:
            self.shields = ShieldHullZones(*ship_definition.get_shield_values)
        self.hull_damage = hull_damage
        self.damage_effects = damage_effects
        self.docked = docked
        self.special_points = special_points

    def get_points(self):
        return self.ship_definition.point_cost + self.special_points + self.upgrades.get_points()

    def move(self, movement, is_navigate=False, is_engine_techs=False):
        if is_engine_techs:
            assert len(movement) == 1 and -2 <= movement[0] <= 2
        else:
            assert self.ship_definition.is_move_legal(movement, is_navigate=is_navigate)
        self.x_pos, self.y_pos, self.angle = movement.move()


class ShipDefinition(object):

    def __init__(self, type, name, size, command_value, squadron_value, engineering_value, defence_tokens, hull,
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
        self.type = type
        self.name = name
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
        movement_speed = len(movement)
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

    def get_shield_values(self):
        return self.shields.values()


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
