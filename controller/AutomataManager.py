from collections import namedtuple
from json import load
from importlib import import_module

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import PoseStamped
    from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
    ROS_AVAILABLE = True
except ModuleNotFoundError:
    ROS_AVAILABLE = False
    print("ROS2 not correctly installed")

Transition = namedtuple("Transaction", ["from_state", "to_state", "with_what", "action"])


def get_pose_stamped(position, navigator):
    if ROS_AVAILABLE:
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = position[0]
        goal_pose.pose.position.y = position[1]
        return goal_pose

    return position


WAREHOUSE_MAP = {
    # Shelf A
    'a': lambda nav: get_pose_stamped((-3.829, -7.604), nav),
    # Shelf B
    'b': lambda nav: get_pose_stamped((-3.791, -3.287), nav),
    # Shelf C
    'c': lambda nav: get_pose_stamped((-3.791, 1.254), nav),
    # Shelf D
    'd': lambda nav: get_pose_stamped((-3.24, 5.861), nav),
    # Dropping zone 'recycling'
    "e": lambda nav: get_pose_stamped((-0.205, 7.403), nav),
    # Dropping zone 'pallet jack'
    "f": lambda nav: get_pose_stamped((-0.073, -8.497), nav),
    # Dropping zone 'conveyor'
    "g": lambda nav: get_pose_stamped((6.217, 2.153), nav),
    # Dropping zone 'freight bay'
    "h": lambda nav: get_pose_stamped((-6.349, 9.147), nav)
}


class AutomataManager:
    special_chars = {"A-Z"}

    def __init__(self, path: str):
        with open(path) as json_file:
            automata_dict = load(json_file)

        self.current_state = automata_dict.get("initial_state")
        self.transitions = [Transition(t.get("from"),
                                       t.get("to"),
                                       t.get("with"),
                                       t.get("action")) for t in automata_dict.get("transitions")]
        self.states = {extract(state)
                       for state in self.transitions
                       for extract in
                       (lambda transition: transition.from_state, lambda transition: transition.to_state)}
        self.alphabet = {transition.with_what for transition in self.transitions} - self.special_chars

        self.message_publisher = {(t.action.get("message").get("type"), t.action.get("message").get("topic")): None for t in self.transitions if t.action and t.action.get("type") == "send_message"}
        if ROS_AVAILABLE:
            rclpy.init()
            self._node = Node("hand_gesture_recognizer")

            for message_type, message_topic in self.message_publisher:
                pkg = ".".join(message_type.split(".")[:-1])
                type_to_import = message_type.split(".")[-1]
                if type_to_import not in globals():
                    globals().update({type_to_import: getattr(import_module(pkg), type_to_import)})

                self.message_publisher[(message_type, message_topic)] = self._node.create_publisher(globals()[type_to_import],
                                                                                                    message_topic,
                                                                                                    10)

            self.navigator = BasicNavigator()

            self.initial_pose = PoseStamped()
            self.initial_pose.header.frame_id = 'map'
            self.initial_pose.header.stamp = self.navigator.get_clock().now().to_msg()
            self.initial_pose.pose.position.x = 0.0
            self.initial_pose.pose.position.y = 0.0
            self.initial_pose.pose.orientation.z = 0.70
            self.initial_pose.pose.orientation.w = 0.71
            self.navigator.setInitialPose(self.initial_pose)

            self.navigator.waitUntilNav2Active()
        else:
            self.navigator = None

    def _get_generic_input(self, specific_input):
        if specific_input not in self.alphabet:
            return "A-Z"
        else:
            return specific_input

    def _navigate_to(self, position):
        if ROS_AVAILABLE:
            self.navigator.goToPose(position)
            i = 0
            while not self.navigator.isTaskComplete():
                i += 1
                feedback = self.navigator.getFeedback()
                if feedback and i % 10 == 0:
                    print(f"Robot is going to position...")

            result = self.navigator.getResult()
            if result == TaskResult.SUCCEEDED:
                print('Goal succeeded!')
            elif result == TaskResult.CANCELED:
                raise Exception('Goal was canceled!')
            elif result == TaskResult.FAILED:
                raise Exception('Goal failed!')
        else:
            print("Navigation to", position)

    def consume_input(self, specific_input):
        input_accepted = True

        # Get all transition from the current state
        transitions_from_current_state = [transition for transition in self.transitions if
                                          transition.from_state == self.current_state]

        # Get the "generic input" from the one given (i.e. a letter becomes "A-Z")
        generic_input = self._get_generic_input(specific_input)

        # Get the transaction that match the given input
        try:
            transition = next(filter(lambda tr: tr.with_what == generic_input, transitions_from_current_state))
        except StopIteration:
            # print(f"Transition not found from {self.current_state} with {generic_input}")
            # Input not accepted for the current state
            return False

        # Update current automata state
        self.current_state = transition.to_state

        # Execute command TODO: from python3.10 use a match-case statement
        if transition.action is None:
            print("No action required")
        elif transition.action.get("type") == "set_navigation_goal":
            raw_position = transition.action.get("coordinate")
            if raw_position == '$with':
                position_callable = WAREHOUSE_MAP.get(specific_input, None)
                if position_callable:
                    position = position_callable(self.navigator)
                else:
                    print(f"Position ({specific_input}) not in database")
                    position = (0, 0)
            else:
                x, y = raw_position.split()
                position = get_pose_stamped((x, y), self.navigator)

            self._navigate_to(position)
        elif transition.action.get("type") == "send_message":
            message = transition.action.get("message")
            message_type = message.get("type")
            message_topic = message.get("topic")
            message_data = message.get("data").replace("$with", specific_input)
            print(f"Sending message {message_type} with data={message_data} to {message_topic}")
        else:
            print("Action not supported")

        return input_accepted
