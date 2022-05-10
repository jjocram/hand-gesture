# Automata manager
The class `AutomataManager` handles the logic of the automaton and uses ROS to communicate with the robot.

## Initialization
```py
def __init__(self, path: str, execute_actions: bool):
    global _initialized # (1)
    self.execute_actions = execute_actions and ROS_AVAILABLE # (2)
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
    self.alphabet = {
        transition.with_what for transition in self.transitions} - self.special_chars

    self.message_publisher = {(t.action.get("message").get("type"), t.action.get("message").get(
        "topic")): None for t in self.transitions if t.action and t.action.get("type") == "send_message"}

    if self.execute_actions:
        if not _initialized:
            rclpy.init()
        self._node = Node("hand_gesture_recognizer")

        for message_type, message_topic in self.message_publisher:
            pkg = ".".join(message_type.split(".")[:-1])
            type_to_import = message_type.split(".")[-1]
            if type_to_import not in globals():
                globals().update({type_to_import: getattr(
                    import_module(pkg), type_to_import)})

            self.message_publisher[(message_type, message_topic)] = self._node.create_publisher(globals()[type_to_import],
                                                                                                message_topic,
                                                                                                10)
        print(self.message_publisher)

        self.navigator = BasicNavigator()

        self.initial_pose = PoseStamped()
        self.initial_pose.header.frame_id = 'map'
        self.initial_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        self.initial_pose.pose.position.x = 0.0
        self.initial_pose.pose.position.y = 0.0
        self.initial_pose.pose.orientation.z = 0.70
        self.initial_pose.pose.orientation.w = 0.71
        if not _initialized:
            self.navigator.setInitialPose(self.initial_pose)

            self.navigator.waitUntilNav2Active()
    else:
        self.navigator = None
    _initialized = True
```

1. The `global` variable `_initialized` is used to avoid a double initialization of `rclpy`
2. `execute_actions` is `True` if the user wants it **and** ROS is available on the system 

In the `__init__` function the automaton is initialized. First of all the configuration file is read and temporarily saved into a `dict`. Then automaton information are extracted from it:
- `current_state`: initially it is the `initial_state`
- `transitions`: the list of transitions saved into `NamedTuple`s
- `states`: the set of states is extracted from the list of transitions
- `alphabet`: the automaton's alphabet is extracted from the transitions and then the set of special elements is removed from it
- `message_publisher`: dictionary that map the type of a message and the topic with a ROS' publisher (it will initialized later)

Then, if the automaton has to execute the actions, the init function will create the correct environment:

1. It will call `#!python rclpy.init()` exactly once
2. It will create the Node that will communicate with others
3. It will parse from the transitions and import the packages required to send message_publisher
4. It will create the message publisher one for each pair of (type, topic)
5. It will initialize the navigator
6. It will create the initial position of the robot
7. It will set the initial position and will wait until the navigator will be ready

## Communicate with the robot
```py
def _navigate_to(self, position):
    if self.execute_actions:
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

def _send_message(self, publisher_identifier, message_fields):
    print(publisher_identifier)
    print(self.message_publisher)
    if self.execute_actions:
        message_type = publisher_identifier[0].split(".")[-1] # (1)
        message = globals()[message_type]() # (2)
        for mf in message_fields:
            setattr(message, mf, message_fields[mf])
        self.message_publisher[publisher_identifier].publish(message)
    else:
        print(
            f"Publishing message: {publisher_identifier}, {message_fields}")
```

1. Extraction of the type of the message to send
2. Creation of the object of the correct type

### Navigate to a position
The function `_navigate_to(self, position)` will handle the navigation to a given `PoseStamped`. First of all the `goToPose` of the object `self.navigator` is called and then, until the task is complete it will receive a feedback from the navigator. The Task can end in 3 ways:

- Succeeded: everything went fine and the robot reached its goal
- Canceled: the user has canceled the task
- Failed: the robot couldn't reach its goal

### Send a message
The function `_send_message(self, publisher_identifier, message_fields)` will handle the sending of messages. The message type is extracted from the `publisher_identifier` and then it is used to create a new object with that type `#!python message = globals()[message_type]()`. Then the method `setattr` is used to add the fields necessary for the message. Finally the right publisher is used to send the message.

## Consume input
Them main purpose of the automaton is consuming the user input and reacting to certain inputs. The function `consume_input(self, specific_input)` handle this purpose.
```py
def consume_input(self, specific_input) -> bool:
    input_accepted = True

    # Get all transition from the current state
    transitions_from_current_state = [transition for transition in self.transitions if
                                      transition.from_state == self.current_state]

    # Get the "generic input" from the one given (i.e. a letter becomes "A-Z")
    generic_input = self._get_generic_input(specific_input)

    # Get the transaction that match the given input
    try:
        transition = next(filter(lambda tr: tr.with_what
                          == generic_input, transitions_from_current_state))
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
            if specific_input in WAREHOUSE_MAP.keys():
                position = self._get_pose_stamped(WAREHOUSE_MAP.get(specific_input))
            else:
                print(f"Position ({specific_input}) not in database")
                position = None
        else:
            x, y = raw_position.split()
            position = self._get_pose_stamped((x, y))

        if position:
            self._navigate_to(position)
    elif transition.action.get("type") == "send_message":
        message = transition.action.get("message")
        message_type = message.get("type")
        message_topic = message.get("topic")
        message_fields = message.get("fields")
        for mf in message_fields:
            message_fields[mf] = message_fields[mf].replace(
                "$with", specific_input)
        self._send_message(publisher_identifier=(message_type, message_topic),
                           message_fields=message_fields)
    else:
        print("Action not supported")

    return input_accepted
```

First of all it identify the correct transition. If none is found then it returns `#!python False`. Otherwise it checks its action type:

### No action:
If no action is to be performed then the function will simply return `input_accepted`

### Set navigation goal
In this case the coordinate field is check for the `$with`. If it there is, then, the specific user input is used (e.g. the letter of the alphabet to identify a position). Otherwise the coordinates are taken from the `coordinate` field of the action.

### Send a message
In this case the different component necessary to create and send the message are extracted from the action and every `$with` found inside a field is replaced with the specific input that triggered the transition. 

## Utility function
### Get `PoseStamped`
```py
def _get_pose_stamped(self, position):
    if self.execute_actions:
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = position[0]
        goal_pose.pose.position.y = position[1]
        return goal_pose

    return position
```

Create an object of type `PoseStamped` given a pair of coordinates as input.

### Get generic input
```py
def _get_generic_input(self, specific_input):
    if specific_input not in self.alphabet:
        return "A-Z"
    else:
        return specific_input
```
Given the user input it will check if it is a special input that must be parsed.
