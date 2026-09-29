#!/usr/bin/env python3
"""Record a rosbag of the standard MediNav topic set."""
from __future__ import annotations

import argparse
import datetime
import os
import time

import rosbag2_py
from rclpy.serialization import serialize_message
from rosidl_runtime_py.utilities import get_message

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile


TOPICS = [
    ('/scan', 'sensor_msgs/msg/LaserScan'),
    ('/imu', 'sensor_msgs/msg/Imu'),
    ('/odom', 'nav_msgs/msg/Odometry'),
    ('/tf', 'tf2_msgs/msg/TFMessage'),
    ('/tf_static', 'tf2_msgs/msg/TFMessage'),
    ('/medi/status', 'medinav_task/msg/MissionStatus'),
    ('/medi/safety_state', 'std_msgs/msg/String'),
    ('/cmd_vel', 'geometry_msgs/msg/Twist'),
    ('/camera/image_raw', 'sensor_msgs/msg/Image'),
]


class BagRecorder(Node):
    def __init__(self, out_uri: str):
        super().__init__('record_run')
        self.n = 0
        self.writer = rosbag2_py.SequentialWriter()
        storage_opts = rosbag2_py.StorageOptions(uri=out_uri, storage_id='sqlite3')
        conv_opts = rosbag2_py.ConverterOptions(
            input_serialization_format='cdr',
            output_serialization_format='cdr',
        )
        self.writer.open(storage_opts, conv_opts)

        for topic, type_str in TOPICS:
            try:
                self.writer.create_topic(
                    rosbag2_py.TopicMetadata(
                        name=topic, type=type_str,
                        serialization_format='cdr',
                    )
                )
                msg_type = get_message(type_str)
                self.create_subscription(
                    msg_type, topic,
                    lambda m, t=topic, ty=type_str: self.on_msg(t, ty, m),
                    QoSProfile(depth=20),
                )
            except Exception as e:
                self.get_logger().warn(f'skip {topic}: {e}')

    def on_msg(self, topic, type_str, msg):
        self.writer.write(topic, serialize_message(msg), self.get_clock().now().nanoseconds)
        self.n += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='')
    ap.add_argument('--duration', type=float, default=60.0)
    args = ap.parse_args()

    out = args.out or os.path.join(
        'bags',
        datetime.datetime.now().strftime('medinav_%Y%m%d_%H%M%S'),
    )
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)

    rclpy.init()
    node = BagRecorder(out)
    t0 = time.monotonic()
    while time.monotonic() - t0 < args.duration:
        rclpy.spin_once(node, timeout_sec=0.1)
    print(f'recorded {node.n} msgs -> {out}')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
