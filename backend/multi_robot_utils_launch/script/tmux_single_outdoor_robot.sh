#!/bin/bash


SESSION_NAME=slide_slam_nodes
BAG_PLAY_RATE=0.5
BAG_DIR="${SLIDE_SLAM_BAG_DIR:-/opt/bags/vems-slam-bags/all_slide_slam_public_demos/outdoor}"

CURRENT_DISPLAY=${DISPLAY}
if [ -z ${DISPLAY} ];
then
  echo "DISPLAY is not set"
  CURRENT_DISPLAY=:0
fi

if [ -z ${TMUX} ];
then
  TMUX= tmux new-session -s $SESSION_NAME -d
  echo "Starting new session."
else
  echo "Already in tmux, leave it first."
  exit
fi

SETUP_ROS_STRING="test -f install/setup.bash && source install/setup.bash || true"

# Make mouse useful in copy mode
tmux setw -g mouse on


tmux new-window -t $SESSION_NAME -n "Main"
tmux split-window -h -t $SESSION_NAME
tmux select-pane -t $SESSION_NAME:1.0
tmux split-window -v -t $SESSION_NAME
tmux select-pane -t $SESSION_NAME:1.3
tmux split-window -v -t $SESSION_NAME
tmux select-pane -t $SESSION_NAME:1.0
tmux split-window -h -t $SESSION_NAME
tmux select-pane -t $SESSION_NAME:1.3
tmux split-window -h -t $SESSION_NAME
# tmux select-pane -t $SESSION_NAME:1.2
# tmux split-window -h -t $SESSION_NAME
# tmux select-pane -t $SESSION_NAME:1.6
# tmux split-window -h -t $SESSION_NAME
# tmux select-pane -t $SESSION_NAME:1.6
# tmux split-window -h -t $SESSION_NAME
tmux select-pane -t $SESSION_NAME:1.0
tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 2; ros2 launch scan2shape_launch infer_node.launch.py" Enter
tmux select-pane -t $SESSION_NAME:1.1
tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 2; ros2 launch object_modeller sync_semantic_measurements.launch.py robot_name:=robot0 odom_topic:=/Odometry" Enter
tmux select-pane -t $SESSION_NAME:1.2
tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 2; ros2 launch sloam single_robot_sloam_test_LiDAR.launch.py enable_rviz:=true" Enter
tmux select-pane -t $SESSION_NAME:1.3
tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 2; ros2 launch scan2shape_launch process_cloud_node_outdoor_with_ns.launch.py" Enter
tmux select-pane -t $SESSION_NAME:1.4
tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 2; ros2 launch scan2shape_launch run_flio_with_driver.launch.py" Enter
tmux select-pane -t $SESSION_NAME:1.5
tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 10; cd $BAG_DIR && ros2 bag play outdoor-falcon4* --clock -r $BAG_PLAY_RATE --start-offset 0 --topics /os_node/lidar_packets /os_node/imu_packets /os_node/metadata" Enter
# tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 2; cd $BAG_DIR && ros2 bag play robot4*.bag -r $BAG_PLAY_RATE --topics /Odometry /robot0/semantic_meas_sync_odom /Odometry:=/robot4/odom /robot0/semantic_meas_sync_odom:=/robot4/semantic_meas_sync_odom" Enter
# tmux select-pane -t $SESSION_NAME:1.5
# tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 2; cd $BAG_DIR && ros2 bag play robot5*.bag -r $BAG_PLAY_RATE --topics /Odometry /robot0/semantic_meas_sync_odom /Odometry:=/robot5/odom /robot0/semantic_meas_sync_odom:=/robot5/semantic_meas_sync_odom" Enter
# tmux select-pane -t $SESSION_NAME:1.6
# tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 2; cd $BAG_DIR && ros2 bag play robot6*.bag -r $BAG_PLAY_RATE --topics /Odometry /robot0/semantic_meas_sync_odom /Odometry:=/robot6/odom /robot0/semantic_meas_sync_odom:=/robot6/semantic_meas_sync_odom" Enter
# tmux select-pane -t $SESSION_NAME:1.7
# tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING; sleep 2; cd $BAG_DIR && ros2 bag play robot7*.bag --topics /Odometry /robot0/semantic_meas_sync_odom /Odometry:=/robot7/odom /robot0/semantic_meas_sync_odom:=/robot7/semantic_meas_sync_odom" Enter
# tmux select-pane -t $SESSION_NAME:1.8
# tmux send-keys -t $SESSION_NAME "$SETUP_ROS_STRING;" Enter
tmux select-layout -t $SESSION_NAME tiled



# Add window to easily kill all processes
tmux new-window -t $SESSION_NAME -n "Kill"
tmux send-keys -t $SESSION_NAME "tmux kill-session -t ${SESSION_NAME}"


tmux select-window -t $SESSION_NAME:1
tmux -2 attach-session -t $SESSION_NAME
