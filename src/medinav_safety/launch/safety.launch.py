#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='medinav_safety',
            executable='safety_supervisor',
            name='safety_supervisor',
            output='screen',
            parameters=[{
                'min_voltage_v': 10.5,
                'warn_voltage_v': 11.0,
                'proximity_stop_m': 0.18,
                'proximity_slow_m': 0.40,
                'slow_scale': 0.35,
            }],
        ),
    ])
