#!/usr/bin/env python3
"""Publish simulated ultrasonic range array (4 corners).

Real hardware: replace with HC-SR04 / ToF array driver publishing same topic.
"""
from __future__ import annotations

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range, Temperature

# topic name -> (frame, yaw rad, min, max)  — names match URDF macros
SENSORS = {
    'ultrasonic/front': ('ultrasonic_front_link', 0.0, 0.02, 4.0),
    'ultrasonic/rear':  ('ultrasonic_rear_link', math.pi, 0.02, 4.0),
    'ultrasonic/fl':    ('ultrasonic_fl_link', math.radians(35), 0.02, 4.0),
    'ultrasonic/fr':    ('ultrasonic_fr_link', math.radians(-35), 0.02, 4.0),
    'ultrasonic/rl':    ('ultrasonic_rl_link', math.radians(145), 0.02, 4.0),
    'ultrasonic/rr':    ('ultrasonic_rr_link', math.radians(-145), 0.02, 4.0),
}


class UltrasonicSim(Node):
    def __init__(self):
        super().__init__('ultrasonic_sim')
        self.declare_parameter('publish_rate_hz', 20.0)
        self.declare_parameter('default_range', 4.0)
        self.declare_parameter('noise_std', 0.01)
        self.pubs = {}
        for topic, (frame, _yaw, rmin, rmax) in SENSORS.items():
            self.pubs[topic] = self.create_publisher(Range, topic, 10)
        rate = float(self.get_parameter('publish_rate_hz').value)
        self.create_timer(1.0 / max(rate, 1.0), self.tick)

    def tick(self):
        default = float(self.get_parameter('default_range').value)
        for topic, (frame, _yaw, rmin, rmax) in SENSORS.items():
            msg = Range()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = frame
            msg.radiation_type = Range.ULTRASOUND
            msg.field_of_view = math.radians(30)
            msg.min_range = rmin
            msg.max_range = rmax
            msg.range = default
            self.pubs[topic].publish(msg)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(UltrasonicSim())


if __name__ == '__main__':
    main()
