import math
from util import Point, limits, abs_angle_to_bearing, MovableNewtonObject
from sub_module import SubModule
from sonar import Sonar
import random
from sub_navigation import Navigation


class ShipFactory():
    @staticmethod
    def create_player_sub(sea):
        print("Creating Player Submarine")
        sub = Submarine(sea)
        sub.name = "Mautilus"
        return sub

    @staticmethod
    def create_simple_sub(sea, pos):
        sub = Submarine(sea)
        sub.set_speed(1)
        sub.deep = random.randint(50, 300)
        sub.set_destination(Point(random.randint(0, 60), random.randint(0, 60)))
        sub.pos = pos
        return sub


class Submarine(MovableNewtonObject):
    MAX_TURN_RATE_SECOND = math.radians(15)/60  # max 15 degrees per minute

    def __init__(self, sea):
        MovableNewtonObject.__init__(self)
        self.messages = []
        self.sea = sea
        self.max_hull_integrity = 100  # in "damage points"
        self.hull_integrity = self.max_hull_integrity
        self.damages = None
        self.deep = 0
        self.message_stop = False

        # build ship
        self.nav = Navigation(self)
        self.comm = Communication(self)
        self.tma = TMA(self)
        self.sonar = Sonar(self)
        self.weapon = Weapon(self)


    # "stop" means the turn just stop because requeres pilot atention
    def add_message(self, module, msg, stop=False):
        self.messages.append("{0}: {1}".format(module, msg))
        self.message_stop = self.message_stop or stop

    def get_messages(self):
        return self.messages, self.message_stop

    def clear_messages(self):
        self.messages = []
        self.message_stop = False

    def get_deep(self):
        return self.deep

    def stop_moving(self):
        self.nav.stop_all()

    # Navigation
    def set_destination(self, dest):
        self.nav.set_destination(dest)

    def set_speed(self, new_speed):
        self.nav.set_speed(new_speed)

    def set_sub_rudder(self, angle):
        angle = limits(angle, -self.MAX_TURN_RATE_SECOND, self.MAX_TURN_RATE_SECOND)
        self.rudder = angle

    def turn(self, time_elapsed):
        self.turn(time_elapsed)
        self.nav.turn(time_elapsed)
        self.comm.turn(time_elapsed)
        self.sonar.turn(time_elapsed)
        self.tma.turn(time_elapsed)
        self.weapon.turn(time_elapsed)

    def get_pos(self):
        return self.pos


class TMA(SubModule):
    def __init__(self, sub):
        SubModule.__init__(self, sub)
        self.module_name = "TMA"


class Weapon(SubModule):
    def __init__(self, sub):
        SubModule.__init__(self, sub)
        self.module_name = "WEAPON"


class Torpedo():
    pass


class Communication(SubModule):
    def __init__(self, sub):
        SubModule.__init__(self, sub)
        self.module_name = "COMM"



