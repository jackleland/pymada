
FRONT_ARC = 'front'
LEFT_ARC = 'left'
RIGHT_ARC = 'right'
REAR_ARC = 'rear'


class Ship(object):

    def __init__(self, ship_definition, x_pos, y_pos, angle, speed, upgrades, defence_tokens, command_tokens, damage=0,
                 damage_effects=None, docked=None, special_points=None):
        self.ship_definition = ship_definition
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.angle = angle
        self.speed = speed
        self.upgrades = upgrades
        self.defence_tokens = defence_tokens
        self.command_tokens = command_tokens
        self.damage = damage
        self.damage_effects = damage_effects
        self.docked = docked
        self.special_points = special_points

    def get_points(self):
        return self.ship_definition.point_cost + self.special_points + self.upgrades.get_points()

    def move(self, movement):
        assert self.ship_definition.is_move_legal(movement)
        self.x_pos, self.y_pos, self.angle = movement.move()


class ShipDefinition(object):

    def __init__(self, type, name, command_value, squadron_value, engineering_value, defence_tokens, hull, shields, arcs,
                 movements, anti_squadron, point_cost, upgrade_slots):
        """

        :param type:
        :param name:
        :param command_value:
        :param squadron_value:
        :param engineering_value:
        :param defence_tokens:
        :param hull:
        :param shields:
        :param arcs:
        :param movements:           dictionary of {speed:max_yaw} with added max speed attribute
        :param anti_squadron:
        :param point_cost:
        :param upgrade_slots:
        """
        self.type = type
        self.name = name

        self.command_value = command_value
        self.squadron_value = squadron_value
        self.engineering_value = engineering_value

        self.defence_tokens = defence_tokens
        self.hull = hull
        self.shields = shields
        self.arcs = arcs
        self.anti_squadron = anti_squadron
        self.movements = movements

        self.point_cost = point_cost
        self.upgrade_slots = upgrade_slots

    def is_move_legal(self, movement, is_navigate=False):
        if movement.speed > self.movements.
        for move_speed, move_yaw in movement.items
        return movement in self.movements
