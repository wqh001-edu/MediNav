#!/usr/bin/env python3
"""Aggregate sensor rates to a compact /medi/sensor_summary topic."""
from __future__ import annotations

from collections import deque

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from sensor_msgs.msg import Imu, Image, JointState, LaserScan, Range


class SensorAggregator(Node):
    def __init__(self):
        super().__init__('sensor_aggregator')
        self.rates = {}
        self.stamps = {}
        self.declare_parameter('window_sec', 2.0)
        self.declare_parameter('rate_hz', 1.0)

        pairs = [
            ('scan', '/scan', LaserScan),
            ('imu', '/imu', Imu),
            ('joint_states', '/joint_states', JointState),
            ('camera', '/camera/image_raw', Image),
            ('us_front', 'ultrasonic/front', Range),
            ('us_fl', 'ultrasonic/fl', Range),
            ('us_fr', 'ultrasonic/fr', Range),
            ('us_rl', 'ultrasonic/rl', Range),
            ('us_rr', 'ultrasonic/rr', Range),
            ('us_rear', 'ultrasonic/rear', Range),
        ]
        for key, topic, mtype in pairs:
            self.stamps[key] = deque(maxlen=200)
            self.create_subscription(
                mtype, topic, lambda _m, k=key: self._on(k), 20
            )

        self.pub = self.create_publisher(String, '/medi/sensor_summary', 10)
        self.create_timer(1.0 / float(self.get_parameter('rate_hz').value), self.publish)

    def _on(self, key: str):
        now = self.get_clock().now().nanoseconds * 1e-9
        self.stamps[key].append(now)

    def publish(self):
        now = self.get_clock().now().nanoseconds * 1e-9
        window = float(self.get_parameter('window_sec').value)
        parts = []
        for key, q in self.stamps.items():
            n = sum(1 for t in q if now - t <= window)
            hz = n / window if window > 0 else 0.0
            parts.append(f'{key}={hz:.1f}')
        msg = String()
        msg.data = ' '.join(parts)
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(SensorAggregator())


if __name__ == '__main__':
    main()
