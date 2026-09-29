#!/usr/bin/env python3
"""Launch delivery task node."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('medinav_task')
    poi = LaunchConfiguration('poi_yaml')
    auto_load = LaunchConfiguration('auto_load')
    auto_unload = LaunchConfiguration('auto_unload')

    return LaunchDescription([
        DeclareLaunchArgument('poi_yaml', default_value=''),
        DeclareLaunchArgument('auto_load', default_value='true'),
        DeclareLaunchArgument('auto_unload', default_value='true'),
        Node(
            package='medinav_task',
            executable='task_node',
            name='medi_task',
            output='screen',
            parameters=[{
                'poi_yaml': poi,
                'auto_load': auto_load,
                'auto_unload': auto_unload,
                'use_sim_time': True,
            }],
        ),
    ])
