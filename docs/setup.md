---
hide:
  - navigation
---
# Setup and configuration

## Requirements
- Python >= 3.8 with pip
- ROS Galactic Geochelone (to test the system with a robot)
- NAV2
- Gazebo (to test the system with a robot)
- TurtleBot3 Gazebo plugin

## Setup the environment
Clone the repository and install the dependencies
### Clone the repository
```bash
git clone git@github.com:jjocram/hand-gesture.git
```

### Install the requirements (you can use a virtual-environment)
```bash
pip install -r requirements.txt
```

## Prepare the simulation environment
### TurtleBot3
Follow the instruction to install the package available on their [website](https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/).

In particular export the robot model to use it in Gazebo
```bash
export GAZEBO_MODEL_PATH="PATH_TO_TURTLEBOT3_WORKSPACE/src/turtlebot3_simulations/turtlebot3_gazebo/models"
```
and the robot model
```bash
export TURTLEBOT3_MODEL=waffle_pi
```

### Gazebo world
You can choose between an empty world and a pre-built warehouse world. Nothing stops you from creating your world.

#### AWS small warehouse
This is the one mainly used for testing. It is a complex environment developed by amazon

##### Clone the repository
```bash
git clone https://github.com/aws-robotics/aws-robomaker-small-warehouse-world.git
```

##### Export the model
```bash
export GAZEBO_MODEL_PATH="PATH_TO_THE_AWS_REPOSITORY/models:$GAZEBO_MODEL_PATH"
```
!!! warning "Check the variable GAZEBO_MODEL_PATH"
    Check that the environment variable GAZEBO_MODEL_PATH has both the path of the TurtleBot3 model and AWS warehouse

##### Add the Waffle Pi in the AWS small warehouse world
Edit the file `PATH_TO_THE_AWS_REPOSITORY/worlds/no_roof_small_warehouse.world` adding
```xml
<include>
    <uri>model://turtlebot3_waffle_pi</uri>
</include>
```
After last `<model>...</model>` and before  `<light>...</light>`

##### Edit the launch file
Edit the file `PATH_TO_TURTLEBOT3_WORKSPACE/src/turtlebot3_simulations/turtlebot3_gazebo/launch/turtlebot3_house.launch.py` replacing
```python
world_file_name = 'turtlebot3_houses/' + TURTLEBOT3_MODEL + '.model'
world = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'worlds', world_file_name)
```
with
```python
world = "PATH_TO_THE_AWS_REPOSITORY/worlds/no_roof_small_warehouse.world"
```

