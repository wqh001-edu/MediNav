#!/usr/bin/env python3
"""Scenario regression evaluator for MediNav.

Runs orders against /medi/order and monitors /medi/status.

Usage:
  python3 tools/eval_scenarios.py --scenarios scenarios
  python3 tools/eval_scenarios.py --ward ward_3 --repeat 3
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass, asdict
from typing import List, Optional

try:
    import rclpy
    from rclpy.node import Node
    from medinav_task.srv import Order
    from medinav_task.msg import MissionStatus
except ImportError:
    print('ERROR: source ROS 2 + workspace first (scripts/ros_env.sh)')
    sys.exit(2)


@dataclass
class TrialResult:
    scenario: str
    ward: str
    success: bool
    elapsed_sec: float
    final_state: str
    message: str


class EvalNode(Node):
    def __init__(self):
        super().__init__('eval_scenarios')
        self.status_state = 'IDLE'
        self.status_detail = ''
        self.elapsed = 0.0
        self.create_subscription(MissionStatus, '/medi/status', self.on_status, 10)
        self.cli = self.create_client(Order, '/medi/order')
        if not self.cli.wait_for_service(timeout_sec=10.0):
            raise RuntimeError('/medi/order not available — is sim_full running?')

    def on_status(self, msg: MissionStatus):
        self.status_state = msg.state
        self.status_detail = msg.detail
        self.elapsed = msg.elapsed_sec

    def run_order(self, ward: str, timeout_sec: float) -> TrialResult:
        req = Order.Request()
        req.ward = ward
        req.order_id = ''
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        res = future.result()
        if not res or not res.accepted:
            return TrialResult(ward, ward, False, 0.0, 'REJECTED',
                               res.message if res else 'no response')

        t0 = time.monotonic()
        while time.monotonic() - t0 < timeout_sec:
            rclpy.spin_once(self, timeout_sec=0.2)
            if self.status_state in ('DONE', 'ERROR'):
                break
        elapsed = time.monotonic() - t0
        ok = self.status_state == 'DONE'
        return TrialResult(ward, ward, ok, elapsed, self.status_state, self.status_detail)


def parse_simple_scenarios(path: str) -> List[dict]:
    """Parse multi-doc YAML-ish scenarios without hard dependency issues."""
    import yaml
    results = []
    with open(path, 'r', encoding='utf-8') as f:
        for doc in yaml.safe_load_all(f):
            if doc:
                results.append(doc)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scenarios', default='scenarios')
    ap.add_argument('--ward', default='')
    ap.add_argument('--repeat', type=int, default=1)
    ap.add_argument('--timeout', type=float, default=120.0)
    ap.add_argument('--out', default='tools/eval_results.csv')
    args = ap.parse_args()

    wards = []
    if args.ward:
        wards = [args.ward] * args.repeat
    else:
        if os.path.isdir(args.scenarios):
            for name in sorted(os.listdir(args.scenarios)):
                if name.endswith(('.yaml', '.yml')):
                    for sc in parse_simple_scenarios(os.path.join(args.scenarios, name)):
                        wards.append(sc.get('ward', 'ward_3'))
        elif os.path.isfile(args.scenarios):
            for sc in parse_simple_scenarios(args.scenarios):
                wards.append(sc.get('ward', 'ward_3'))
        else:
            wards = ['ward_1', 'ward_3', 'ward_4']

    rclpy.init()
    node = EvalNode()
    rows: List[TrialResult] = []
    for w in wards:
        node.get_logger().info(f'running {w} ...')
        row = node.run_order(w, args.timeout)
        rows.append(row)
        print(f'  -> success={row.success} t={row.elapsed_sec:.1f}s state={row.final_state}')

    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()) if rows else
                                ['scenario', 'ward', 'success', 'elapsed_sec', 'final_state', 'message'])
        writer.writeheader()
        for r in rows:
            writer.writerow(asdict(r))

    n_ok = sum(1 for r in rows if r.success)
    print(f'\nRESULT {n_ok}/{len(rows)} success -> {args.out}')
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if n_ok == len(rows) and rows else 1)


if __name__ == '__main__':
    main()
