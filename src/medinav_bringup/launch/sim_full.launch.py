#!/usr/bin/env python3
"""Full MediNav stack: Gazebo + robot + Nav2 + task + perception mock."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


def generate_launch_description():
    pkg_gazebo = get_package_share_directory('medinav_gazebo')
    pkg_nav = get_package_share_directory('medinav_navigation')
    pkg_task = get_package_share_directory('medinav_task')
    pkg_perc = get_package_share_directory('medinav_perception')
    pkg_sensors = get_package_share_directory('medinav_sensors')
    pkg_safety = get_package_share_directory('medinav_safety')

    use_sim_time = LaunchConfiguration('use_sim_time')

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo, 'launch', 'sim_world.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )

    # Nav2 after robot + controllers settle
    nav = TimerAction(
        period=8.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_nav, 'launch', 'navigation.launch.py')
                ),
                launch_arguments={'use_sim_time': use_sim_time}.items(),
            )
        ],
    )

    task = TimerAction(
        period=12.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_task, 'launch', 'task.launch.py')
                ),
            )
        ],
    )

    perception = TimerAction(
        period=10.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_perc, 'launch', 'perception.launch.py')
                ),
            )
        ],
    )

    sensors = TimerAction(
        period=9.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_sensors, 'launch', 'sensors.launch.py')
                ),
            )
        ],
    )

    safety = TimerAction(
        period=11.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_safety, 'launch', 'safety.launch.py')
                ),
            )
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        sim,
        nav,
        sensors,
        perception,
        safety,
        task,
    ])
