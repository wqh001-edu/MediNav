#!/usr/bin/env python3
"""Lightweight camera monitor: logs FPS and optionally saves snapshots."""
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class CameraMonitor(Node):
    def __init__(self):
        super().__init__('camera_monitor')
        self.declare_parameter('topic', '/camera/image_raw')
        self.declare_parameter('log_every_sec', 5.0)
        topic = self.get_parameter('topic').value
        self.frames = 0
        self.last_log = time.monotonic()
        self.create_subscription(Image, topic, self.on_img, 10)
        self.get_logger().info(f'monitoring {topic}')

    def on_img(self, msg: Image):
        self.frames += 1
        now = time.monotonic()
        if now - self.last_log >= float(self.get_parameter('log_every_sec').value):
            fps = self.frames / max(now - self.last_log, 1e-3)
            self.get_logger().info(
                f'{msg.width}x{msg.height} fps~{fps:.1f} encoding={msg.encoding}'
            )
            self.frames = 0
            self.last_log = now


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(CameraMonitor())


if __name__ == '__main__':
    main()
