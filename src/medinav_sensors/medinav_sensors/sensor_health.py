#!/usr/bin/env python3
"""Sensor health monitor — diagnostic_updater + /medi/sensor_health."""
from __future__ import annotations

import rclpy
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from diagnostic_updater import DiagnosticTask, Updater
from rclpy.node import Node
from sensor_msgs.msg import Imu, Image, JointState, LaserScan


class TopicRateTask(DiagnosticTask):
    def __init__(self, node: Node, name: str, topic: str, msg_type, min_hz: float, timeout_sec: float = 2.0):
        super().__init__(name)
        self.node = node
        self.topic = topic
        self.min_hz = min_hz
        self.timeout_sec = timeout_sec
        self.count = 0
        self.last_time = None
        self.last_msg_time = None
        node.create_subscription(msg_type, topic, self._cb, 10)

    def _cb(self, _msg):
        now = self.node.get_clock().now().nanoseconds * 1e-9
        self.count += 1
        self.last_msg_time = now

    def run(self, stat):
        now = self.node.get_clock().now().nanoseconds * 1e-9
        if self.last_msg_time is None:
            stat.summary(DiagnosticStatus.ERROR, 'no messages yet')
            return stat
        age = now - self.last_msg_time
        # estimate rate from message ages (simple)
        if age > self.timeout_sec:
            stat.summary(DiagnosticStatus.ERROR, f'timeout age={age:.1f}s')
        else:
            stat.summary(DiagnosticStatus.OK, f'alive age={age:.2f}s count={self.count}')
        stat.add(KeyValue('topic', self.topic))
        stat.add(KeyValue('min_hz', str(self.min_hz)))
        return stat


class SensorHealth(Node):
    def __init__(self):
        super().__init__('sensor_health')
        self.declare_parameter('scan_min_hz', 8.0)
        self.declare_parameter('imu_min_hz', 50.0)
        self.declare_parameter('joint_min_hz', 20.0)

        self.updater = Updater(self)
        self.updater.set_hardware_id('medibot')

        scan_min = float(self.get_parameter('scan_min_hz').value)
        imu_min = float(self.get_parameter('imu_min_hz').value)
        j_min = float(self.get_parameter('joint_min_hz').value)

        self.updater.add(TopicRateTask(self, 'lidar_scan', '/scan', LaserScan, scan_min))
        self.updater.add(TopicRateTask(self, 'imu', '/imu', Imu, imu_min))
        self.updater.add(TopicRateTask(self, 'joint_states', '/joint_states', JointState, j_min))

        # optional camera
        self.updater.add(TopicRateTask(self, 'camera', '/camera/image_raw', Image, 5.0, timeout_sec=5.0))

        self.create_timer(1.0, self.updater.update)
        self.get_logger().info('sensor health monitoring started')


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(SensorHealth())


if __name__ == '__main__':
    main()
