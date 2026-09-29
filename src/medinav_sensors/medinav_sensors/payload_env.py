#!/usr/bin/env python3
"""Payload environment (medicine box) sensors.

Publishes:
  /medi/payload/temperature  sensor_msgs/Temperature
  /medi/payload/humidity     std_msgs/Float32  (relative humidity %)
  /medi/payload/present      std_msgs/Bool     (lock/microswitch)
"""
from __future__ import annotations

import math
import random

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Temperature
from std_msgs.msg import Bool, Float32


class PayloadEnv(Node):
    def __init__(self):
        super().__init__('payload_env')
        self.declare_parameter('temp_c', 22.0)
        self.declare_parameter('humidity_pct', 45.0)
        self.declare_parameter('present', True)
        self.declare_parameter('rate_hz', 2.0)

        self.pub_t = self.create_publisher(Temperature, '/medi/payload/temperature', 10)
        self.pub_h = self.create_publisher(Float32, '/medi/payload/humidity', 10)
        self.pub_p = self.create_publisher(Bool, '/medi/payload/present', 10)
        rate = float(self.get_parameter('rate_hz').value)
        self.create_timer(1.0 / max(rate, 0.1), self.tick)

    def tick(self):
        now = self.get_clock().now().to_msg()
        t = Temperature()
        t.header.stamp = now
        t.header.frame_id = 'payload_link'
        t.temperature = float(self.get_parameter('temp_c').value) + random.gauss(0, 0.05)
        t.variance = 0.1
        self.pub_t.publish(t)

        h = Float32()
        h.data = float(self.get_parameter('humidity_pct').value) + random.gauss(0, 0.2)
        self.pub_h.publish(h)

        p = Bool()
        p.data = bool(self.get_parameter('present').value)
        self.pub_p.publish(p)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(PayloadEnv())


if __name__ == '__main__':
    main()
