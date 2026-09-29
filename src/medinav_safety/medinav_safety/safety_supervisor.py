#!/usr/bin/env python3
"""Safety supervisor.

Watches e-stop, bumper, battery, payload presence, and ultrasonic proximity.
Republishes a safe /cmd_vel (input /cmd_vel_raw -> /cmd_vel) with forced zero
on any hazard. Also publishes /medi/safety_state.

Real robot: wire physical e-stop to both hardware EN and /medi/estop.
"""
from __future__ import annotations

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import BatteryState, Range
from std_msgs.msg import Bool, String


class SafetySupervisor(Node):
    def __init__(self):
        super().__init__('safety_supervisor')
        self.declare_parameter('min_voltage_v', 10.5)
        self.declare_parameter('warn_voltage_v', 11.0)
        self.declare_parameter('proximity_stop_m', 0.18)
        self.declare_parameter('proximity_slow_m', 0.40)
        self.declare_parameter('slow_scale', 0.35)
        self.declare_parameter('use_sim_time', True)

        self.estop = False
        self.bumper = False
        self.voltage = 12.6
        self.payload_ok = True
        self.min_range = 4.0
        self.last_cmd = Twist()

        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_raw = self.create_publisher(Twist, '/cmd_vel_raw', 10)  # echo/debug
        self.pub_state = self.create_publisher(String, '/medi/safety_state', 10)

        self.create_subscription(Twist, '/cmd_vel_nav', self.on_nav_cmd, 10)
        self.create_subscription(Bool, '/medi/estop', self.on_estop, 10)
        self.create_subscription(Bool, '/medi/bumper', self.on_bumper, 10)
        self.create_subscription(BatteryState, '/battery_state', self.on_batt, 10)
        self.create_subscription(Bool, '/medi/payload/present', self.on_payload, 10)
        for t in ('ultrasonic/front', 'ultrasonic/fl', 'ultrasonic/fr'):
            self.create_subscription(Range, t, self.on_range, 10)

        self.create_timer(0.05, self.tick)  # 20 Hz safety loop
        self.get_logger().info('safety supervisor ready')

    def on_nav_cmd(self, msg: Twist):
        self.last_cmd = msg

    def on_estop(self, msg: Bool):
        if msg.data and not self.estop:
            self.get_logger().error('E-STOP asserted')
        self.estop = bool(msg.data)

    def on_bumper(self, msg: Bool):
        if msg.data and not self.bumper:
            self.get_logger().error('BUMPER hit')
        self.bumper = bool(msg.data)

    def on_batt(self, msg: BatteryState):
        if msg.voltage > 0:
            self.voltage = float(msg.voltage)

    def on_payload(self, msg: Bool):
        self.payload_ok = bool(msg.data)

    def on_range(self, msg: Range):
        if math.isfinite(msg.range):
            self.min_range = min(self.min_range, msg.range)

    def tick(self):
        # decay min_range slightly toward max so short flash doesn't stick forever
        self.min_range = min(self.min_range + 0.05, 4.0)

        cmd = Twist()
        hazards = []
        if self.estop:
            hazards.append('estop')
        if self.bumper:
            hazards.append('bumper')
        if self.voltage < float(self.get_parameter('min_voltage_v').value):
            hazards.append('low_battery')

        scale = 1.0
        stop_d = float(self.get_parameter('proximity_stop_m').value)
        slow_d = float(self.get_parameter('proximity_slow_m').value)
        if self.min_range < stop_d:
            hazards.append('proximity_stop')
        elif self.min_range < slow_d:
            scale = float(self.get_parameter('slow_scale').value)
            hazards.append('proximity_slow')

        if not hazards or hazards == ['proximity_slow']:
            cmd = self.last_cmd
            cmd.linear.x *= scale
            cmd.angular.z *= scale

        self.pub_cmd.publish(cmd)
        self.pub_raw.publish(self.last_cmd)

        state = 'OK' if not hazards else ('STOP:' + ','.join(hazards))
        msg = String()
        msg.data = (
            f'{state} v={self.voltage:.2f}V min_range={self.min_range:.2f}m '
            f'payload_ok={self.payload_ok}'
        )
        self.pub_state.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(SafetySupervisor())


if __name__ == '__main__':
    main()
