#!/usr/bin/env python3
"""Nav2 navigation with AMCL using saved hospital map."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('medinav_navigation')
    pkg_nav2 = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': autostart,
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(pkg_nav, 'maps', 'hospital_mini.yaml'),
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_nav, 'config', 'nav2_params.yaml'),
        ),
        DeclareLaunchArgument('autostart', default_value='true'),
        nav2_bringup,
    ])
