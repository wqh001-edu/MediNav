#!/usr/bin/env python3
"""Run a YAML mission: sequence of ward deliveries.

Example mission YAML:
  name: morning_rounds
  legs:
    - ward: ward_1
    - ward: ward_3
    - ward: ward_4
"""
from __future__ import annotations

import argparse
import sys
import time

import rclpy
import yaml
from rclpy.node import Node

from medinav_task.msg import MissionStatus
from medinav_task.srv import Order


class MissionRunner(Node):
    def __init__(self):
        super().__init__('mission_runner')
        self.state = 'IDLE'
        self.elapsed = 0.0
        self.create_subscription(MissionStatus, '/medi/status', self.on_status, 10)
        self.cli = self.create_client(Order, '/medi/order')
        if not self.cli.wait_for_service(timeout_sec=15.0):
            raise RuntimeError('/medi/order unavailable')

    def on_status(self, msg: MissionStatus):
        self.state = msg.state
        self.elapsed = msg.elapsed_sec

    def run_leg(self, ward: str, timeout: float) -> bool:
        req = Order.Request()
        req.ward = ward
        fut = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=5.0)
        res = fut.result()
        if not res or not res.accepted:
            self.get_logger().error(f'order rejected: {res}')
            return False
        self.get_logger().info(f'leg {ward} started ({res.order_id})')
        t0 = time.monotonic()
        while time.monotonic() - t0 < timeout:
            rclpy.spin_once(self, timeout_sec=0.2)
            if self.state in ('DONE', 'ERROR'):
                break
        ok = self.state == 'DONE'
        self.get_logger().info(f'leg {ward} -> {self.state} ({time.monotonic()-t0:.1f}s)')
        return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mission_yaml')
    ap.add_argument('--leg-timeout', type=float, default=120.0)
    args = ap.parse_args()

    with open(args.mission_yaml, 'r', encoding='utf-8') as f:
        mission = yaml.safe_load(f)

    rclpy.init()
    node = MissionRunner()
    ok = 0
    legs = mission.get('legs', [])
    for i, leg in enumerate(legs, 1):
        ward = leg.get('ward', 'ward_3')
        node.get_logger().info(f'[{i}/{len(legs)}] {mission.get("name","mission")} -> {ward}')
        if node.run_leg(ward, args.leg_timeout):
            ok += 1
        time.sleep(float(leg.get('pause_sec', 1.0)))

    print(f'MISSION RESULT {ok}/{len(legs)}')
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if ok == len(legs) and legs else 1)


if __name__ == '__main__':
    main()
