# -*- coding: utf-8 -*-
from sub_module import SubModule
import util
import math
import random


class SonarContact:
    NEW = 'New'
    TRACKING = 'Tracking'
    LOST = 'Lost'

    def __init__(self, sonar_idx, bearing):
        self.sonar_idx = sonar_idx
        self.tracking_status = self.NEW
        self.name = ""
        self.time_tracking = 0
        self.last_seen = None
        self.name = None  # like "i688"
        self.ident = ""  # like S1
        self.obj_type = None
        self.details = None
        self.range = None
        self.bearing = bearing
        self.course = None
        self.speed = None
        self.deep = 0
        self.bands = [0.0] * 10

    def is_new(self):
        return self.tracking_status == self.NEW

    def __str__(self):
        obj_type = self.obj_type if self.obj_type else '<unknown>'
        course = round(self.course) if self.course else '-'
        range_str = round(self.range) if self.range else '-'
        speed = round(self.speed) if self.speed else '-'
        #dist = reference_pos.distance_to(pos)
        #angle = math.degrees(util.abs_angle_to_bearing(reference_pos.angle_to(pos)))
        return "{ident:3} ({ty}) bearing {bearing:d}, range {range:d}, course {course}, speed {speed} {status}".\
            format(ident=self.ident, ty=obj_type, bearing=round(self.bearing), range=self.range,
            course=course, speed=speed, status=self.tracking_status)


class Sonar(SubModule):
    def __init__(self, sub):
        self.module_name = "SONAR"
        self.contacts = {}
        self.sub = sub
        self.sea = sub.sea
        self.counter = 0  # counter for Sierra Contacts
        self.time_for_next_scan = 0

    def return_near_objects(self):
        return self.contacts

    def get_new_contact_id(self):
        self.counter += 1
        return "S{0:3d}".format(self.counter)

    def guess_obj_type(self, bands):
        probs = []
        for known_obj in self.KNOWN_TYPES:
            name = known_obj[0]
            ref_bands = known_obj[1]
            likelihood = util.calc_band_likelihood(ref_bands, bands)
            probs.append((likelihood, name))
        print(probs)
        return probs

    def turn(self, time_elapsed):
        if self.time_for_next_scan <= 0.0:
            # passive scan
            self.passive_scan(time_elapsed)
            self.time_for_next_scan = 60.0
        else:
            self.time_for_next_scan -= time_elapsed

        #if self.mode == self.ACTIVE_SCAN:
        #    self.pulse_scan()

    def passive_scan(self, time_elapsed):
        scan = self.sea.passive_scan(self.sub, time_elapsed)
        for sr in scan:  #
            idx = sr.sonar_idx
            if idx in self.contacts:
                self.update_contact(self.contacts[idx], sr, time_elapsed)
            else:
                self.add_contact(sr)

    def pulse_scan(self):
        pass

    def add_contact(self, scan_result):
        sc = SonarContact(scan_result.sonar_idx, scan_result.bearing)
        sc.bearing = scan_result.bearing
        sc.ident = self.get_new_contact_id()
        self.contacts[scan_result.sonar_idx] = sc
        self.add_message("New contact bearing {0}, designated {1}".format(sc.bearing, sc.name),True)


    def update_contact(self, sc, scan_result, time_elapsed):
        #sc.total_time_elapsed += time_elapsed
        if (sc.total_time_elapsed < 1):
            sc.tracking_status = sc.NEW
        else:
            sc.tracking_status = sc.TRACKING
        sc.time_tracking += time_elapsed
        sc.last_seen = self.sub.sea.time

        #self.name = None  # like "i688"
        #self.ident = ""  # like S1
        #self.obj_type = None
        #self.range = None
        self.bearing = scan_result.bearing
        #self.course = None
        #self.speed = None
        self.deep = 0
        self.bands = [0.0] * 10
        #tracking_obj.tracking_status = SensorContact.TRACKING
        #tracking_obj.time_tracking += time_elapsed
        pass

    def status(self):
        return "Sonar tracking {objs} objects".format(objs=len(self.contacts))
