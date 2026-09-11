#!/usr/bin/env bash
# End-to-end synthetic multi-robot demo (no dataset download needed).
#
# 1. Publishes 3 simulated robots driving through a shared synthetic forest
#    and records them into a small rosbag2 bag (~1 MB).
# 2. Plays the bag into decentralized_sloam_multi_robot_forest.launch.py
#    (headless) using the same topic layout as the tmux demo scripts.
# 3. Asserts all nodes survive and an inter-robot loop closure is found.
#
# Usage: pixi run demo-synthetic   (run from the repository root)
BAGDIR=/tmp/synth_bags/e2e
rm -rf "$BAGDIR"
mkdir -p "$BAGDIR"

# shellcheck disable=SC1091
source install/setup.bash

TOPICS="/robot0/odom /robot1/odom /robot2/odom /robot0/semantic_meas_sync_odom /robot1/semantic_meas_sync_odom /robot2/semantic_meas_sync_odom"

python tools/synth_multi_robot_demo.py --robots 3 --duration 30 &
PUB_PID=$!
sleep 3
# shellcheck disable=SC2086
timeout -s INT 34 ros2 bag record -o "$BAGDIR/synth_forest" $TOPICS \
  > "$BAGDIR/record.log" 2>&1
kill -9 $PUB_PID 2>/dev/null

ros2 launch sloam decentralized_sloam_multi_robot_forest.launch.py \
  enable_rviz:=false > "$BAGDIR/run.log" 2>&1 &
LAUNCH_PID=$!
sleep 8
# shellcheck disable=SC2086
ros2 bag play "$BAGDIR/synth_forest" -r 1.0 --topics $TOPICS \
  > "$BAGDIR/play.log" 2>&1
sleep 35
kill -INT $LAUNCH_PID 2>/dev/null
sleep 5
kill -9 $LAUNCH_PID 2>/dev/null

FAIL=0
if grep -q "process has died" "$BAGDIR/run.log"; then
  echo "FAIL: a sloam node crashed (see $BAGDIR/run.log)"
  FAIL=1
fi
if grep -q "INTER LOOP CLOSURE FOUND" "$BAGDIR/run.log"; then
  echo "PASS: inter-robot loop closure found"
else
  echo "FAIL: no inter-robot loop closure in $BAGDIR/run.log"
  FAIL=1
fi
exit $FAIL
