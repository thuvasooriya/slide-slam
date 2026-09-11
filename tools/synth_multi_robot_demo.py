#!/usr/bin/env python3
"""Synthetic multi-robot demo publisher for SlideSLAM (no bag download needed).

Simulates N robots driving through a shared forest of cylinder (tree)
landmarks. Each robot publishes nav_msgs/Odometry and
sloam_msgs/SemanticMeasSyncOdom in the exact topics the tmux demo scripts
replay (``/robot<id>/odom`` and ``/robot<id>/semantic_meas_sync_odom``).

Usage:
    pixi run python tools/synth_multi_robot_demo.py --robots 3 --duration 25
"""
def make_forest():
    # (x, y) world positions of tree trunks; radius 0.25 m, height along +z.
    pts = [
        (6.4, -0.3), (6.4, 2.5), (7.2, 1.3), (6.8, -3.4), (4.7, -2.8),
        (2.8, -1.9), (5.2, -0.7), (4.0, -4.7), (4.6, -2.9), (5.3, -1.1),
        (4.5, 0.7), (2.3, 1.2), (-3.9, -3.5), (1.5, -4.6), (13.8, -5.9),
        (11.3, -2.6), (14.0, -3.0), (11.8, -13.7), (9.8, -17.0), (11.4, -14.2),
        (11.2, -11.5), (6.9, -16.5), (11.5, -12.6), (5.9, -11.9),
        (0.6, -7.8), (-2.2, -19.1), (-2.0, -17.3), (-1.7, -17.6),
        (-1.9, -19.6), (4.4, -2.9), (3.7, -4.2), (5.1, -1.0),
        (3.3, -1.3), (2.1, 5.5), (6.7, 3.4), (3.4, 7.6),
    ]
    return [(x, y, 0.25) for x, y in pts]
import argparse
import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sloam_msgs.msg import ROSCylinder, SemanticMeasSyncOdom




class SynthRobots(Node):
    def __init__(self, n_robots, rate_hz=10.0):
        super().__init__("synth_multi_robot_demo")
        self.n_robots = n_robots
        # Start poses (x, y, yaw): overlapping views of the same forest.
        self.starts = [(0.0, 0.0, 0.0), (5.8, -6.9, math.pi / 2),
                       (-4.0, 4.0, -math.pi / 4)][:n_robots]
        self.speed = 1.0
        self.t = 0.0
        self.dt = 1.0 / rate_hz
        self.trees = make_forest()
        self.odom_pubs = [
            self.create_publisher(Odometry, f"/robot{i}/odom", 10)
            for i in range(n_robots)
        ]
        self.meas_pubs = [
            self.create_publisher(
                SemanticMeasSyncOdom,
                f"/robot{i}/semantic_meas_sync_odom", 10)
            for i in range(n_robots)
        ]
        self.obs_counter = 0
        self.create_timer(self.dt, self.tick)

    def pose_at(self, i, t):
        x0, y0, yaw = self.starts[i]
        d = self.speed * t
        return (x0 + d * math.cos(yaw), y0 + d * math.sin(yaw), yaw)

    def tick(self):
        self.t += self.dt
        now = self.get_clock().now().to_msg()
        for i in range(self.n_robots):
            x, y, yaw = self.pose_at(i, self.t)
            odom = Odometry()
            odom.header.stamp = now
            odom.header.frame_id = "odom"
            odom.child_frame_id = "base_link"
            odom.pose.pose.position.x = x
            odom.pose.pose.position.y = y
            odom.pose.pose.orientation.z = math.sin(yaw / 2.0)
            odom.pose.pose.orientation.w = math.cos(yaw / 2.0)
            self.odom_pubs[i].publish(odom)
            # 1 Hz semantic observations in the body frame, 30 m range.
            self.obs_counter += 1
            if self.obs_counter % 10 == 0:
                msg = SemanticMeasSyncOdom()
                msg.header.stamp = now
                msg.odometry = odom
                cy, sy = math.cos(yaw), math.sin(yaw)
                for j, (wx, wy, r) in enumerate(self.trees):
                    dx, dy = wx - x, wy - y
                    if dx * dx + dy * dy > 30.0 ** 2:
                        continue
                    c = ROSCylinder()
                    c.root = [dx * cy + dy * sy, -dx * sy + dy * cy, 0.0]
                    c.ray = [0.0, 0.0, 1.0]
                    c.radius = r
                    c.id = j
                    c.semantic_label = 0
                    msg.cylinder_factors.append(c)
                self.meas_pubs[i].publish(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--robots", type=int, default=3)
    ap.add_argument("--duration", type=float, default=25.0)
    args = ap.parse_args()
    rclpy.init()
    node = SynthRobots(args.robots)
    end = node.get_clock().now().nanoseconds / 1e9 + args.duration
    while rclpy.ok() and node.get_clock().now().nanoseconds / 1e9 < end:
        rclpy.spin_once(node, timeout_sec=0.05)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
