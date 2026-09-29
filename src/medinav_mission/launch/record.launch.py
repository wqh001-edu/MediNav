#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


def generate_launch_description():
    bag = LaunchConfiguration('bag')
    return LaunchDescription([
        DeclareLaunchArgument('bag', default_value=''),
        ExecuteProcess(
            cmd=['ros2', 'run', 'medinav_mission', 'record_run',
                 '--out', bag, '--duration', '120'],
            output='screen',
        ),
    ])
