#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    nodes = [
        Node(package='medinav_sensors', executable='ultrasonic_sim',
             name='ultrasonic_sim', output='screen',
             parameters=[{'publish_rate_hz': 20.0, 'default_range': 4.0}]),
        Node(package='medinav_sensors', executable='payload_env',
             name='payload_env', output='screen',
             parameters=[{'temp_c': 22.0, 'humidity_pct': 45.0, 'present': True}]),
        Node(package='medinav_sensors', executable='sensor_aggregator',
             name='sensor_aggregator', output='screen'),
        Node(package='medinav_sensors', executable='sensor_health',
             name='sensor_health', output='screen'),
    ]
    return LaunchDescription(nodes)
