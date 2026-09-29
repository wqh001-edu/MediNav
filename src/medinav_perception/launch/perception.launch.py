#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='medinav_perception',
            executable='mock_digit_reader',
            name='mock_digit_reader',
            output='screen',
            parameters=[{'digit': '3', 'rate_hz': 1.0}],
        ),
        Node(
            package='medinav_perception',
            executable='camera_monitor',
            name='camera_monitor',
            output='screen',
        ),
    ])
