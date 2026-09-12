# Known Issues and Research Caveats (`ros2_dev`)

Carried over from the removed `ROS2_MIGRATION_REPORT.md`. Only items with
experimental consequences are kept here; mechanical port details live in git
history and `tests/`.

## 1. Missing upstream simulation inputs

`closure_retrigger.launch.py` and `sim_perturb_odom.launch.py` reference
scripts that were never committed upstream (`pub_loop_closure_retrigger.py`,
`add_noise_to_ground_truth_odom.py`). Minimal rclpy stubs exist under
`frontend/scan2shape/script/` so the launch graph resolves, but they only log
a warning and are not functional simulators. The simulation yamls
`sloam_sim.yaml`, `sim.yaml`, and `sloam_active_slam_real_robot.yaml` are also
absent upstream.

## 2. `number_of_robots` declaration race

Declared via the guarded `*_declare_or_get` wrapper in three backend files
(`databaseManager.cpp`, `inputNode.cpp`, `sloamNode.cpp`) with conflicting
defaults (`0`, `1`, `1`). First declarer wins at runtime, so always pass it
explicitly from the launch file.

## 3. Open-vocabulary topics are hardcoded

`rgb_segmentation_open_vocab.launch.py` accepts topic overrides, but
`detect_open_vocab.py` builds topic names internally from `robot_name` and
silently ignores them.

## 4. RangeNet++ weight naming

The published `penn_smallest.zip` model contains files with a spurious `.zip`
extension (e.g. `backbone.zip`) that are raw weights. Strip the extension
before pointing `model_dir` at them.

## Workflow conventions

- Bag data is external (multi-GB, not in git). Fetch it headlessly with
  `pixi run python tools/gdrive_key.py download <folder-url> -O <dir>`
  (`tools/gdrive_key.py` sends Drive `resourcekey`s, which stock `gdown`
  cannot — plain `gdown` 401s on these legacy link-shared folders).
- `backend/sloam/clipper_semantic_object/` is vendored third-party and exempt
  from the static checker; its `/home/jiuzhou` example paths are upstream
  dead code, never built (`CLIPPER_BUILD_TESTS=OFF`).
- Verified without bag data: `check-port` (55/55), `pytest` (470 passed,
  3 skipped), `test-place-recognition` (11 inliers, 0.34 overlap, loop closure
  found), `launch-smoke` (63/63, requires sourced `install/setup.bash`).

## Fixed during verification (synthetic end-to-end runs)

- Missing `/sloam` node namespace: ROS1 ran the node under
  `NodeHandle("sloam")`, but the port constructed `rclcpp::Node("sloam")`
  with no namespace. Relative `odom` resolved to `/odom` (shared by all
  robots) instead of `/sloam/odom`, so the launch remap to
  `/robot<id>/odom` never matched and no odometry ever arrived. Fixed in
  `backend/sloam/src/core/inputNode.cpp` (`Node("sloam", "sloam")`).
- Throttle-clock segfault: `RCLCPP_*_THROTTLE` with a throwaway
  `*rclcpp::Clock::make_shared()` crashed every node on first execution
  with data (exit -11 in `CylinderMapManager::InLoopClosureRegion`).
  Replaced with function-static clocks in `cylinderMapManager.cpp` and
  `factorgraph/graph.cpp`.
- `demo-synthetic` (`pixi run demo-synthetic`, `tools/synth_e2e.sh`) now
  covers the full loop without downloads: 3 robots, inter-loop closures
  found for pairs 1-0 and 2-0, zero crashes.
- Model weights: the current `penn_smallest.zip` upload already ships
  extensionless PyTorch weight files, so the README's `.zip`-rename step
  is a no-op for this copy.
