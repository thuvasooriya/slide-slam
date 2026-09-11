# SlideSLAM

> [!NOTE]
> ## Looking for ROS2 support?
>
> This `master` branch is the **ROS1 Noetic** (Ubuntu 20.04) version of SlideSLAM — the version used to produce the results in our paper and the most
battle-tested setup.
>
> An experimental **ROS2 Jazzy Jalisco** (Ubuntu 24.04) port lives on the [`ros2_dev`](https://github.com/KumarRobotics/SLIDE_SLAM/tree/ros2_dev) branch.
It has not been as extensively tested as this `master` branch, but is provided to help developers who want to use SlideSLAM with ROS2.

This repository contains the source code for the project SlideSLAM: Sparse, Lightweight, Decentralized Metric-Semantic SLAM for Multi-Robot Navigation.
- More details can be found on the [project website](https://xurobotics.github.io/slideslam/).
- Our paper is available on arXiv [here](https://arxiv.org/abs/2406.17249).

# Table of contents
- [SlideSLAM](#slideslam)
- [Table of contents](#table-of-contents)
- [Quickstart with Pixi (Recommended)](#quickstart-with-pixi-recommended)
- [Run our demos (with processed data)](#run-our-demos-with-processed-data)
  - [Download example data](#download-example-data)
  - [What these demos will do](#what-these-demos-will-do)
  - [Run multi-robot demo (based on LiDAR data)](#run-multi-robot-demo-based-on-lidar-data)
- [Run on raw sensor data (RGBD or LiDAR bags)](#run-on-raw-sensor-data-rgbd-or-lidar-bags)
  - [Download example data](#download-example-data-1)
  - [Run our RGBD data experiments](#run-our-rgbd-data-experiments)
  - [Run our LiDAR Data experiments](#run-our-lidar-data-experiments)
- [Troubleshoot](#troubleshoot)
- [Acknowledgement](#acknowledgement)
- [Citation](#citation)




# Quickstart with Pixi (Recommended)

SlideSLAM on ROS 1 Noetic can be run via [Pixi](https://pixi.sh) using `conda-forge` and `robostack`. Workspace dependencies (ROS 1 Noetic, GTSAM, PCL, OpenCV, Eigen 3.4, Sophus, Qhull) are managed locally without modifying system packages or requiring Docker.

### 1. Install Pixi / mise
```bash
curl -fsSL https://pixi.sh/install.sh | bash
# or if you use mise:
mise use -g pixi
```

### 2. Clone & Build
```bash
git clone https://github.com/thuvasooriya/slide-slam.git
cd slide-slam

# Install dependencies:
pixi install

# Initialize workspace configuration (first time only):
pixi run config

# Build all ROS 1 Noetic packages in parallel:
pixi run build
```

### 3. Verify & Run Tests
```bash
# Run the place recognition verification test:
pixi run test
```

Note: demo bags are multi-GB downloads and are not checked into git. Point the
demo scripts at your download via `export SLIDE_SLAM_BAG_DIR=/path/to/bags`
(defaults to `/opt/bags/...`). `pixi run test` needs no bag data.

# Run our demos (with processed data)
Note: if the access to any of the links is lost, please contact the authors, and we will provide the data from our lab's NAS.

This section will guide you through running our demos with processed data. We provide processed data in the form of rosbags that contains only the odometry and semantic measurements (i.e. object observations). Running the entire pipeline containing object detection and the rest of SLAM for multiple robots simultaneously onboard one computer is computationally and memory intensive. 

**Note:** Such tests can to a large degree replicate what would happen onboard the robot since when you run real world multi-robot experiment, each robot will only be responsible for processing its own data, and the processed data shared by the other robots in the form provided by here. 

## Download example data

Please download the processed data bags from [this link](https://drive.google.com/drive/folders/0B5oeNvHFA8WDfjVMa29HSldseF81SUxFMTA4d3F6VlN2YW9hdlZ0RzNMM1V3TGdJZmRMb1E?resourcekey=0-E7OTjCMZq2C58dps4Gibqw&usp=sharing). This containes compact processed bags for forest and urban outdoor environments. Please use the right data with the right scripts as specified below.


## What these demos will do
- Intermittent communication between robot nodes at a fixed time interval. 
- Multiple robots running on the same computer, and therefore, the computational load is going to be (num_robots multiplied by the computation load of each robot during actual experiment).

## Run multi-robot demo (based on LiDAR data)
**First, please refer to the section above and make sure you have everything built.**

**Option 1:** Use our tmux script (recommended)

Navigate to the `script` folder inside the `multi_robot_utils_launch` package (or enter `pixi shell` first):
```bash
cd backend/multi_robot_utils_launch/script
```

Modify `tmux_multi_robot_with_bags_forest.sh` to set the `BAG_DIR` to where you downloaded the bags

Modify `BAG_PLAY_RATE` to your desired play rate (lower than 1.0 if you have a low-specification CPU)

Then make it executable if needed
```
chmod +x tmux_multi_robot_with_bags_forest.sh
```

Finally, execute this script
```
./tmux_multi_robot_with_bags_forest.sh
```

If you want to terminate this program, go to the last terminal window and press `Enter` to kill all the tmux sessions.

**Option 2:** If you prefer not to use this tmux script, please refer to the `roslaunch` commands inside this tmux script and execute those commands by yourself.

**To run the same above example with urban outdoor data, use the `tmux_multi_robot_with_bags_parking_lot.sh` script and repeat the above steps.**

# Run on raw sensor data (RGBD or LiDAR bags)
This section will guide you through running our code stack with raw sensor data, which is rosbags containing LiDAR-based or RGBD-based data. Note: size of these raw bags are usually anywhere from 10-100 GB.

## Download example data

Please download the LiDAR demo bags from [this link](https://drive.google.com/drive/folders/0B5oeNvHFA8WDfjVMa29HSldseF81SUxFMTA4d3F6VlN2YW9hdlZ0RzNMM1V3TGdJZmRMb1E?resourcekey=0-E7OTjCMZq2C58dps4Gibqw&usp=sharing). It is present inside the `outdoor` folder.

Please download the RGBD demo bags from [this link](https://drive.google.com/drive/folders/0B5oeNvHFA8WDfjVMa29HSldseF81SUxFMTA4d3F6VlN2YW9hdlZ0RzNMM1V3TGdJZmRMb1E?resourcekey=0-E7OTjCMZq2C58dps4Gibqw&usp=sharing). It is present inside the `indoor` folder.

Please download the KITTI benchmark processed bags from [this link](https://drive.google.com/drive/folders/0B5oeNvHFA8WDfjVMa29HSldseF81SUxFMTA4d3F6VlN2YW9hdlZ0RzNMM1V3TGdJZmRMb1E?resourcekey=0-E7OTjCMZq2C58dps4Gibqw&usp=sharing). It is present inside the `kitti_bags` folder.

Please download our trained RangeNet++ model from [this link](https://drive.google.com/drive/folders/0B5oeNvHFA8WDfjVMa29HSldseF81SUxFMTA4d3F6VlN2YW9hdlZ0RzNMM1V3TGdJZmRMb1E?resourcekey=0-E7OTjCMZq2C58dps4Gibqw&usp=sharing). It is currently named `penn_smallest.zip`. Follow the instructions in the `Run our LiDAR data experiments`  section below on how to use this model.

## Run our RGBD data experiments

**Option 1:** Use our tmux script (recommended)

Navigate to the `script` folder inside the `multi_robot_utils_launch` package (or enter `pixi shell` first):
```bash
cd backend/multi_robot_utils_launch/script
```

Modify `tmux_single_indoor_robot.sh` to set the `BAG_DIR` to where you downloaded the bags

Modify `BAG_PLAY_RATE` to your desired play rate (lower than 1.0 if you have a low-specification CPU)

Then make it executable if needed
```
chmod +x tmux_single_indoor_robot.sh
```

Finally, if you want to use Yolo-v8, execute this script
```
./tmux_single_indoor_robot.sh
```


**IMPORTANT**: If it is your first time to run this script, the front-end instance segmentation network will download the weights from the internet. This may take a while depending on your internet speed. Once this is finished, kill all the tmux sessions (see below) and re-run the script.

If you want to terminate this program, go to the last terminal window and press `Enter` to kill all the tmux sessions.

**Option 2:** If you prefer not to use this tmux script, please refer to the `roslaunch` commands inside this tmux script and execute those commands by yourself, or using the detailed instructions found [here](https://github.com/XuRobotics/SLIDE_SLAM/wiki#run-rgbd-raw-bags-detailed-instructions).

## Run our LiDAR Data experiments

**Download the LiDAR semantic segmentation RangeNet++ model**
```
(1) Download the model from the above link.
(2) Unzip the file and place the model in a location of your choice.
(3) Open the extracted model folder and make sure that there are no files inside having a .zip extension. If there are, then rename ALL OF THEM to remove the .zip extension. For example backbone.zip should be renamed to backbone
```

**Option 1:** Use our tmux script (recommended)

Make sure you edit the ```infer_node_params.yaml``` file present inside the ```scan2shape_launch/config``` folder and set the value of ```model_dir``` param to point to the path to the RangeNet++ model you downloaded in the previous step. Make sure to compelte the path with the ```/``` at the end.

Navigate to the `script` folder inside the `multi_robot_utils_launch` package (or enter `pixi shell` first):
```bash
cd backend/multi_robot_utils_launch/script
```

Modify `tmux_single_outdoor_robot.sh` to set the `BAG_DIR` to where you downloaded the bags

Modify `BAG_PLAY_RATE` to your desired play rate (lower than 1.0 if you have a low-specification CPU)

Then make it executable if needed
```
chmod +x tmux_single_outdoor_robot.sh
```

Finally, execute this script
```
./tmux_single_outdoor_robot.sh
```

If you want to terminate this program, go to the last terminal window and press `Enter` to kill all the tmux sessions.

**Option 2:** If you prefer not to use this tmux script, please refer to the `roslaunch` commands inside this tmux script and execute those commands by yourself, or using the detailed instructions found [here](https://github.com/XuRobotics/SLIDE_SLAM/wiki#run-lidar-raw-bags-detailed-instructions).

## Run KITTI Benchmark experiments

**Option 1:** Use our tmux script

Navigate to the `script` folder inside the `multi_robot_utils_launch` package (or enter `pixi shell` first):
```bash
cd backend/multi_robot_utils_launch/script
```

Modify `tmux_single_outdoor_kitti.sh` to set the `BAG_DIR` to where you downloaded the bags

Then make it executable if needed
```
chmod +x tmux_single_outdoor_kitti.sh
```

Finally, execute this script
```
./tmux_single_outdoor_kitti.sh
```

If you want to terminate this program, go to the last terminal window and press `Enter` to kill all the tmux sessions.

# Troubleshoot
**Rate of segmentation:**
- When running on your own data, we recommend to throttle the segmentation topic (segmented point cloud or images) rate to 2-4 Hz to avoid computation delay in the front end, especially if you’re experiencing performance issues at higher rates. Please also update the `expected_segmentation_frequency` parameter in the corresponding `process_cloud_node_*_params.yaml` file as well as the `desired_frequency` in the `infer_node_params.yaml` to the actual rate of the topic. 

# Acknowledgement
We use GTSAM as the backend. We thank [Guilherme Nardari](linkedin.com/in/guilherme-nardari-23ba91a8) for his contributions to this repository. 

# Citation
If you find our system or any of its modules useful for your academic work, we would appreciate it if you could cite our work as follows:
```
@article{liu2024slideslam,
  title={Slideslam: Sparse, lightweight, decentralized metric-semantic slam for multi-robot navigation},
  author={Liu, Xu and Lei, Jiuzhou and Prabhu, Ankit and Tao, Yuezhan and Spasojevic, Igor and Chaudhari, Pratik and Atanasov, Nikolay and Kumar, Vijay},
  journal={arXiv preprint arXiv:2406.17249},
  year={2024}
}
```
