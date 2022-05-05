---
hide:
  - navigation
---

# Run the simulation
After the [setup of the environment](setup.md) you can run the simulation how many times you want.
## Launch the Gazebo world
### Empty world
```bash
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

### AWS small warehouse
```bash
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py
```

## Launch the Nav2 system
```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=PATH_TO_THE_MAP
```
!!! info "Map of the environment"
    The map of the warehouse is available on the repository of this project. You can create the map for your environments.

## Launch the hand gesture recognizer
Inside the directory of the repository
```bash
python3 main.py --interactive
```
The `--interactive` argument start the program asking to the user how they want to use it. If you prefer to use the operational mode remove the argument.
