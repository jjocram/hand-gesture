from collections import namedtuple
from json import load
from sys import exit

try:
    from geometry_msgs.msg import PoseStamped
    from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
except ModuleNotFoundError:
    print("ROS2 not correctly installed")

Transaction = namedtuple("Transaction", ["from_state", "to_state", "with_what", "action"])


def get_pose_stamped(position, navigator):
    """
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = position[0]
    goal_pose.pose.position.y = position[1]
    return goal_pose
    """
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
    # Dropping zone 'conveyer'
    "g": lambda nav: get_pose_stamped((6.217, 2.153), nav),
    # Dropping zone 'frieght bay'
    "h": lambda nav: get_pose_stamped((-6.349, 9.147), nav)
}


class AutomataManager:
    special_chars = {"A-Z"}

    def __init__(self, path: str, navigator):
        with open(path) as json_file:
            automata_dict = load(json_file)

        self.current_state = automata_dict.get("initial_state")
        self.transitions = [Transaction(t.get("from"),
                                        t.get("to"),
                                        t.get("with"),
                                        t.get("action")) for t in automata_dict.get("transitions")]
        self.states = {extract(state)
                       for state in self.transitions
                       for extract in
                       (lambda transition: transition.from_state, lambda transition: transition.to_state)}
        self.alphabet = {transition.with_what for transition in self.transitions} - self.special_chars
        self.navigator = navigator

    def _get_generic_input(self, specific_input):
        if specific_input not in self.alphabet:
            return "A-Z"
        else:
            return specific_input

    def _navigate_to(self, position):
        print("Navigation to", position)
        """
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
        """

    def consume_input(self, specific_input):
        # Get all transition from the current state
        transitions_from_current_state = [transition for transition in self.transitions if
                                          transition.from_state == self.current_state]

        # Get the "generic input" from the one given (i.e. a letter becomes "A-Z")
        generic_input = self._get_generic_input(specific_input)

        # Get the transaction that match the given input
        try:
            transition = next(filter(lambda tr: tr.with_what == generic_input, transitions_from_current_state))
        except StopIteration:
            print(f"Transition not found from {self.current_state} with {specific_input}")
            exit(1)

        print(transition)

        # Update current automata state
        self.current_state = transition.to_state

        # Execute command
        match transition.action:
            case {"type": "set_navigation_goal", "coordinate": raw_position}:
                if raw_position == '$with':
                    position = WAREHOUSE_MAP[specific_input](self.navigator)
                else:
                    x, y = raw_position.split()
                    position = get_pose_stamped((x, y), self.navigator)
                self._navigate_to(position)
            case {"type": "send_message", "message": message}:
                message_type = message.get("type")
                message_data = message.get("data").replace("$with", specific_input)
                print(f"Sending message {message_type} with data={message_data}")
            case None:
                print("No action required")
            case _:
                print("Action not supported")
