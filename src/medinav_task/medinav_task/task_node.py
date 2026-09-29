#!/usr/bin/env python3
"""MediBot delivery task node.

State machine (aligned with 2026 送药小车 semantics):
  IDLE -> TO_PHARMACY -> WAIT_LOAD -> TO_WARD -> WAIT_UNLOAD -> RETURNING -> DONE
"""
from __future__ import annotations

import math
import time
import uuid
from enum import Enum
from typing import Optional

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from medinav_task.poi_map import PoiMap, Pose2D

from medinav_task.msg import MissionStatus
from medinav_task.srv import LoadMedicine, Order


class State(str, Enum):
    IDLE = 'IDLE'
    TO_PHARMACY = 'TO_PHARMACY'
    WAIT_LOAD = 'WAIT_LOAD'
    TO_WARD = 'TO_WARD'
    WAIT_UNLOAD = 'WAIT_UNLOAD'
    RETURNING = 'RETURNING'
    DONE = 'DONE'
    ERROR = 'ERROR'


class TaskNode(Node):
    def __init__(self):
        super().__init__('medi_task')
        self.cb_group = ReentrantCallbackGroup()

        self.declare_parameter('poi_yaml', '')
        self.declare_parameter('auto_load', True)          # skip manual load for pure sim
        self.declare_parameter('auto_unload', True)
        self.declare_parameter('load_timeout_sec', 20.0)
        self.declare_parameter('unload_timeout_sec', 30.0)
        self.declare_parameter('nav_timeout_sec', 120.0)
        self.declare_parameter('goal_xy_tol', 0.18)
        self.declare_parameter('goal_yaw_tol', 0.35)
        self.declare_parameter('settle_sec', 0.5)

        poi_yaml = self.get_parameter('poi_yaml').get_parameter_value().string_value
        self.poi = PoiMap(poi_yaml or None)
        self.auto_load = self.get_parameter('auto_load').value
        self.auto_unload = self.get_parameter('auto_unload').value

        self.state = State.IDLE
        self.order_id = ''
        self.ward = ''
        self.t0 = 0.0
        self._nav_goal_handle = None
        self._nav_result_ok = False
        self._wait_until = 0.0
        self._auto_advanced = False

        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose',
                                       callback_group=self.cb_group)
        self.status_pub = self.create_publisher(MissionStatus, '/medi/status', 10)
        self.create_service(Order, '/medi/order', self.on_order, callback_group=self.cb_group)
        self.create_service(LoadMedicine, '/medi/load', self.on_load, callback_group=self.cb_group)

        self.create_timer(0.5, self.publish_status, callback_group=self.cb_group)
        self.get_logger().info(
            f'Task node ready. POIs={self.poi.names()} auto_load={self.auto_load}'
        )

    # ---------------- services ----------------
    def on_order(self, req, res):
        if self.state not in (State.IDLE, State.DONE, State.ERROR):
            res.accepted = False
            res.order_id = self.order_id
            res.message = f'busy in state {self.state.value}'
            return res

        ward = req.ward.strip() or 'ward_3'
        try:
            self.poi.get(ward)
        except KeyError as e:
            res.accepted = False
            res.order_id = ''
            res.message = str(e)
            return res

        self.order_id = req.order_id or uuid.uuid4().hex[:8]
        self.ward = ward
        self.t0 = time.monotonic()
        res.accepted = True
        res.order_id = self.order_id
        res.message = f'order accepted -> {ward}'
        self.get_logger().info(res.message)
        self.set_state(State.TO_PHARMACY)
        return res

    def on_load(self, req, res):
        if self.state != State.WAIT_LOAD:
            res.success = False
            res.message = f'not in WAIT_LOAD (state={self.state.value})'
            return res
        if req.order_id and req.order_id != self.order_id:
            res.success = False
            res.message = 'order_id mismatch'
            return res
        res.success = True
        res.message = f'loaded {req.mass_kg:.2f} kg'
        self.get_logger().info(res.message)
        self.set_state(State.TO_WARD)
        return res

    # ---------------- state machine ----------------
    def set_state(self, new: State):
        self.get_logger().info(f'STATE {self.state.value} -> {new.value}')
        self.state = new
        self._auto_advanced = False
        self.publish_status()
        # drive transitions
        if new == State.TO_PHARMACY:
            self.navigate_to(self.poi.get('pharmacy'), next_state=State.WAIT_LOAD)
        elif new == State.WAIT_LOAD:
            self._wait_until = time.monotonic() + float(self.get_parameter('load_timeout_sec').value)
        elif new == State.TO_WARD:
            self.navigate_to(self.poi.get(self.ward), next_state=State.WAIT_UNLOAD)
        elif new == State.WAIT_UNLOAD:
            self._wait_until = time.monotonic() + float(self.get_parameter('unload_timeout_sec').value)
        elif new == State.RETURNING:
            self.navigate_to(self.poi.get('pharmacy'), next_state=State.DONE)
        elif new in (State.DONE, State.ERROR, State.IDLE):
            self._nav_next = None

    def navigate_to(self, pose: Pose2D, next_state: State):
        self._nav_next = next_state
        self._nav_result_ok = False

        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('navigate_to_pose action server not available')
            self.set_state(State.ERROR)
            return

        goal = NavigateToPose.Goal()
        goal.pose = self.to_pose_stamped(pose)
        self.get_logger().info(
            f'Navigate to ({pose.x:.2f}, {pose.y:.2f}, yaw={pose.yaw:.2f}) next={next_state.value}'
        )
        send_future = self.nav_client.send_goal_async(
            goal, feedback_callback=self.on_nav_feedback
        )
        send_future.add_done_callback(self.on_nav_goal_response)

    def on_nav_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error('nav goal rejected')
            self.set_state(State.ERROR)
            return
        self._nav_goal_handle = handle
        handle.get_result_async().add_done_callback(self.on_nav_result)

    def on_nav_feedback(self, msg):
        # distance remaining is useful for progress; NavigateToPose feedback
        try:
            d = msg.feedback.distance_remaining
            self.get_logger().debug(f'remaining={d:.2f} m')
        except Exception:
            pass

    def on_nav_result(self, future):
        result = future.result()
        status = result.status
        ok = status == GoalStatus.STATUS_SUCCEEDED
        self._nav_result_ok = ok
        if not ok:
            self.get_logger().error(f'nav finished with status={status}')
            # still transition for sim robustness if close enough; else error
            if status in (GoalStatus.STATUS_CANCELED, GoalStatus.STATUS_ABORTED):
                self.set_state(State.ERROR)
                return
        if self._nav_next is not None:
            self.set_state(self._nav_next)

    # ---------------- timers / helpers ----------------
    def publish_status(self):
        msg = MissionStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.order_id = self.order_id
        msg.ward = self.ward
        msg.state = self.state.value
        msg.elapsed_sec = float(time.monotonic() - self.t0) if self.t0 else 0.0
        msg.progress = self.estimate_progress()
        msg.detail = ''
        self.status_pub.publish(msg)

        # wait-state handling (auto mode / timeout)
        if self.state in (State.WAIT_LOAD, State.WAIT_UNLOAD):
            if self.state == State.WAIT_LOAD and self.auto_load and not self._auto_advanced:
                self._auto_advanced = True
                self.get_logger().info('auto_load -> skip WAIT_LOAD')
                self.set_state(State.TO_WARD)
                return
            if self.state == State.WAIT_UNLOAD and self.auto_unload and not self._auto_advanced:
                self._auto_advanced = True
                self.get_logger().info('auto_unload -> skip WAIT_UNLOAD')
                self.set_state(State.RETURNING)
                return
            if time.monotonic() > self._wait_until:
                self.get_logger().warn(f'{self.state.value} timeout')
                if self.state == State.WAIT_LOAD:
                    self.set_state(State.ERROR)
                else:
                    self.set_state(State.RETURNING)

    def estimate_progress(self) -> float:
        order = [
            State.IDLE, State.TO_PHARMACY, State.WAIT_LOAD,
            State.TO_WARD, State.WAIT_UNLOAD, State.RETURNING, State.DONE,
        ]
        try:
            return order.index(self.state) / float(len(order) - 1)
        except ValueError:
            return 0.0

    def to_pose_stamped(self, p: Pose2D) -> PoseStamped:
        msg = PoseStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.x = float(p.x)
        msg.pose.position.y = float(p.y)
        msg.pose.position.z = 0.0
        msg.pose.orientation.z = math.sin(p.yaw / 2.0)
        msg.pose.orientation.w = math.cos(p.yaw / 2.0)
        return msg


def main(args=None):
    rclpy.init(args=args)
    node = TaskNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
