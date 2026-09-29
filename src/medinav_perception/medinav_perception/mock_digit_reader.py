#!/usr/bin/env python3
"""Mock digit reader.

Publishes a target ward on /medi/digit for simulation.
In real hardware, replace with OpenMV / camera pipeline.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MockDigitReader(Node):
    def __init__(self):
        super().__init__('mock_digit_reader')
        self.declare_parameter('digit', '3')
        self.declare_parameter('rate_hz', 1.0)
        self.pub = self.create_publisher(String, '/medi/digit', 10)
        rate = float(self.get_parameter('rate_hz').value)
        self.create_timer(1.0 / max(rate, 0.1), self.tick)

    def tick(self):
        digit = str(self.get_parameter('digit').value)
        msg = String()
        msg.data = digit
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MockDigitReader()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
