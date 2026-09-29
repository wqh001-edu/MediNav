#!/usr/bin/env python3
"""Fleet coordinator for 1–2 MediBots.

Single-robot mode: passthrough.
Two-robot mode: corridor mutual exclusion + relay pause rule (≥ pause_gap_m).

Topics (namespaced robots):
  /robot_1/odom  /robot_2/odom
  /robot_1/cmd_vel_nav  /robot_2/cmd_vel_nav  ->  /robot_N/cmd_vel
  /medi/fleet_state
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import String


@dataclass
class RobotState:
    name: str
    x: float = 0.0
    y: float = 0.0
    yaw: float = 0.0
    has_pose: bool = False


class FleetCoordinator(Node):
    def __init__(self):
        super().__init__('fleet_coordinator')
        self.declare_parameter('robot_names', ['robot_1', 'robot_2'])
        self.declare_parameter('pause_gap_m', 0.70)
        self.declare_parameter('corridor_y_half_width', 0.8)
        self.declare_parameter('x_overlap_m', 1.2)

        names = self.get_parameter('robot_names').value
        self.robots = {n: RobotState(n) for n in names}
        self.cmds = {n: Twist() for n in names}

        for n in names:
            self.create_subscription(
                Odometry, f'/{n}/odom', lambda msg, k=n: self.on_odom(k, msg), 10
            )
            self.create_subscription(
                Twist, f'/{n}/cmd_vel_nav', lambda msg, k=n: self.on_cmd(k, msg), 10
            )
            self.create_publisher(Twist, f'/{n}/cmd_vel', 10)

        self.pub_state = self.create_publisher(String, '/medi/fleet_state', 10)
        self.out_pubs = {n: self.create_publisher(Twist, f'/{n}/cmd_vel', 10) for n in names}

        self.create_timer(0.05, self.tick)
        self.get_logger().info(f'fleet coordinator robots={names}')

    def on_odom(self, name: str, msg: Odometry):
        r = self.robots[name]
        r.x = msg.pose.pose.position.x
        r.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        # yaw from quaternion
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        r.yaw = math.atan2(siny_cosp, cosy_cosp)
        r.has_pose = True

    def on_cmd(self, name: str, msg: Twist):
        self.cmds[name] = msg

    def tick(self):
        names = list(self.robots.keys())
        block = set()
        gap = float(self.get_parameter('pause_gap_m').value)
        half_w = float(self.get_parameter('corridor_y_half_width').value)
        x_ov = float(self.get_parameter('x_overlap_m').value)

        if len(names) >= 2:
            a, b = self.robots[names[0]], self.robots[names[1]]
            if a.has_pose and b.has_pose:
                dist = math.hypot(a.x - b.x, a.y - b.y)
                same_corridor = abs(a.y) < half_w and abs(b.y) < half_w
                x_close = abs(a.x - b.x) < x_ov
                # trailing robot is the one with larger x if moving -x direction,
                # or simply the second robot if first is ahead on -x path.
                # Rule from 送药赛题: rear vehicle must keep gap and may pause.
                if same_corridor and x_close and dist < gap:
                    # block the robot with greater x (behind when traveling -x)
                    rear = names[0] if a.x > b.x else names[1]
                    block.add(rear)

        for n in names:
            cmd = self.cmds[n]
            if n in block:
                stopped = Twist()
                self.out_pubs[n].publish(stopped)
            else:
                self.out_pubs[n].publish(cmd)

        msg = String()
        msg.data = f'block={sorted(block)} robots={names}'
        self.pub_state.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(FleetCoordinator())


if __name__ == '__main__':
    main()
