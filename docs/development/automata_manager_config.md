# Automaton configuration
To configure the automaton i sufficient write a JSON file and give its path to the controllers that will use it.

## Basic structure
The basic structure of the JSON file is
```json
{
  "initial_state": "string",
  "transitions": ["Transitions"]
}
```

## Transition
A transition is triggered when the automaton is in a state that accept the gesture. When a transition is triggered an action is executed. The structure of a transition is:
```json
{
      "from": "string",
      "to": "string",
      "with": "string",
      "action": {...}
    }
```

- `from`: the state the automaton must be in to accept the input and trigger the action
- `to`: the state the automaton will be after executing the action
- `with`: the element of the alphabet that trigger the action
- `action`: the action to perform when the transition is triggered

### Action - do nothing
When `#!json "action": null` nothing is performed when the transition is triggered.

### Action - send a message
To publish a message on a topic you can use this action:
```json
{
    "type": "send_message",
    "message": {
        "type": "string",
        "topic": "string",
        "fields": {
            ...
        }
    }
}
```

- `message.type`: the type of the message you want to send. It must the complete `#!python import` path. E.g. `#!json "type": "std_msgs.msg.String"` will import `String` from `std_msgs.msg`
- `message.topic`: the topic on which the message will be published
- `message.fields`: the data fields to use to build the message. E.g. `#!json "data": "data to send"` will be converted into `#!python message.data = "data to send"`

### Action - set a navigation goal
To set a *Nav 2* navigation goal you can use this action:
```json
"action": {
    "type": "set_navigation_goal",
    "coordinate": "string"
}
```

- `coordinate` is the position to reach

### Text interpolation for data
You can use the keyword `$with` that will be substitute at run-time with the content of the `with` field of the transition. It is useful in particular, when the trigger is a set of elements of the alphabet. E.g. the set of the letters `[Aa-Zz]`.
