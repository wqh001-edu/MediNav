#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg = get_package_share_directory('medinav_fleet')
    return LaunchDescription([
        Node(
            package='medinav_fleet',
            executable='fleet_coordinator',
            name='fleet_coordinator',
            output='screen',
            parameters=[os.path.join(pkg, 'config', 'fleet.yaml')],
        ),
    ])
