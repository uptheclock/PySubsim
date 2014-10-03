# -*- coding: utf-8 -*-
import math
from util import abs_angle_to_bearing, Bands, limits
from physic import Point, MovableNewtonObject
from sub_module import SubModule
from sonar import Sonar
from sound import db
from linear_scale import linear_scaler
import random
from sub_navigation import Navigation


class ShipFactory():
    @staticmethod
    def create_player_sub(sea):
        print("Creating Player Submarine")
        sub = Submarine(sea, kind='688')
        sub.pos = Point(10, 10)
        sub.name = "Mautilus"
        sea.add_submarine(sub)
        return sub

    @staticmethod
    def create_simple_sub(sea, pos):
        sub = Submarine(sea)
        sub.set_speed(1)
        sub.actual_deep = random.randint(50, 300)
        sub.set_destination(Point(random.randint(0, 60), random.randint(0, 60)))
        sub.pos = pos
        return sub


class Submarine(MovableNewtonObject):
    MAX_TURN_RATE_HOUR = math.radians(35)*60  # max 35 degrees per minute
    MAX_DEEP_RATE_FEET = 1   # 1 foot per second

    def __init__(self, sea, kind):
        MovableNewtonObject.__init__(self)
        self.kind = kind
        self.messages = []
        self.sea = sea
        self.max_hull_integrity = 100  # in "damage points"
        self.hull_integrity = self.max_hull_integrity
        self.damages = None
        self.actual_deep = 150
        self.set_deep = 150
        self.message_stop = False
        self.cavitation = False


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

    def stop_moving(self):
        self.nav.stop_all()

    # non-liner noise:
    # for 0 < speed < 15 :  linear from 40 to 60
    # for speed > 15 : linear with factor of 2db for each knot
    # ref: http://fas.org/man/dod-101/navy/docs/es310/uw_acous/uw_acous.htm
    NOISE_RANGE1 = linear_scaler([0,15],[40,60])
    NOISE_RANGE2 = linear_scaler([15,35],[60,100])
    def self_noise(self): # returns
        #
        """
        Assumes the noise is proportional to speed

        Cavitation:

        Cavitation occurs when the propeller is spinning so fast water bubbles at
        the blades' edges. If you want to go faster, go deeper first. Water
        pressure at deeper depth reduces/eliminates cavitation.

        If you have the improved propeller upgrade, you can go about 25% faster
        without causing cavitation.

        Rule of thumb: number of feet down, divide by 10, subtract 1, is the
        fastest speed you can go without cavitation.

        For example, at 150 feet, you can go 14 knots without causing cavitation.
        150/10 = 15, 15-1 = 14.

        You can get the exact chart at the Marauders' website. (url's at the end of
          the document)


        :return: sound in in decibels
        """
        if self.speed <= 15:
            noise = self.NOISE_RANGE1(self.speed)
        else:
            noise = self.NOISE_RANGE2(self.speed)

        # cavitation doesn't occur with spd < 7
        max_speed_for_deep = max((self.actual_deep / 10) - 1, 7)
        cavitating = max_speed_for_deep < self.speed

        if cavitating and not self.cavitation:
            self.add_message("SONAR","COMM, SONAR: CAVITATING !!!", True)

        self.cavitation = cavitating

        return db(noise + (100 if cavitating else 0) + random.gauss(0,0.4))

    # Navigation
    def set_destination(self, dest):
        self.nav.set_destination(dest)

    def set_speed(self, new_speed):
        self.nav.speed = new_speed

    def set_sub_rudder(self, angle):
        angle = limits(angle, -self.MAX_TURN_RATE_HOUR, self.MAX_TURN_RATE_HOUR)
        self.rudder = angle

    def rudder_right(self):
        self.rudder = self.MAX_TURN_RATE_HOUR

    def rudder_left(self):
        self.rudder = -self.MAX_TURN_RATE_HOUR

    def rudder_center(self):
        self.rudder = 0

    def turn(self, time_elapsed):
        MovableNewtonObject.turn(self, time_elapsed)
        # deep
        deep_diff = self.set_deep - self.actual_deep
        if abs(deep_diff) > 0.1:
            dive_rate = min(deep_diff, self.MAX_DEEP_RATE_FEET)
            self.actual_deep += dive_rate * time_elapsed * 3600


        self.nav.turn(time_elapsed)
        self.comm.turn(time_elapsed)
        self.sonar.turn(time_elapsed)
        self.tma.turn(time_elapsed)
        self.weapon.turn(time_elapsed)

    def get_pos(self):
        assert isinstance(self.pos, Point)
        return self.pos

    def __str__(self):
        return "Submarine: {status}  deep:{deep:.0f}({sdeep})".format(status=MovableNewtonObject.__str__(self),
                                                                  deep=self.actual_deep,sdeep=self.set_deep)


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



