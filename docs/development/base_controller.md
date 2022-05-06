# Base controller
As base class there is the `BaseController`. It manages:

- The thread to avoid duplicate messages
- The interaction with the automaton
- The choice of the gesture (between static and dynamic)

## Get gesture
This function get one gesture from the two buffers given as input. The precedence is given to the dynamic gesture. This decision has been taken because a dynamic gesture requires an action by the operator. Instead, a static one is always recognized.
```py
def _get_gesture(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer):
    static_gesture = None
    static_gesture_id = static_gesture_buffer.get_gesture()
    if static_gesture_id is not None and static_gesture_id != -1:
        if self.last_static != static_gesture_id:
            # print("Static gesture id:", static_gesture_id)
            self.last_static = static_gesture_id

        if self.last_static != -1:
            static_gesture = self.static_gesture_map.get(self.last_static, None)

    dynamic_gesture = None
    dynamic_gesture_id = dynamic_gesture_buffer.get_gesture()
    if dynamic_gesture_id is not None and dynamic_gesture_buffer != -1:
        if self.last_dynamic != dynamic_gesture_id:
            # print("Dynamic gesture id:", dynamic_gesture_id)
            self.last_dynamic = dynamic_gesture_id
            dynamic_gesture = self.dynamic_gesture_map.get(self.last_dynamic, None)

    return dynamic_gesture if dynamic_gesture else static_gesture
```

## Consume gesture
The method `_consume_gesture` manage the access to the automaton using a `Lock`. In this way only one gesture at a time can be given as input to the automaton. Moreover, it ignore the `static` dynamic gesture. Finally, if the gesture is accepted by the automaton it calls a callback and wait for `4` seconds before releasing the `Lock`.
```py
def _consume_gesture(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer, input_accepted_callback: callable):
    with self.sending_message:
        input_gesture = self._get_gesture(static_gesture_buffer, dynamic_gesture_buffer)
        if input_gesture and input_gesture != "static":
            input_accepted = self.automata.consume_input(input_gesture)
            if input_accepted:
                if input_accepted_callback:
                    input_accepted_callback(input_gesture)
                sleep(4)
```

The `consume_gesture` method must be implemented by the sub-classes.
```py 
def consume_gesture(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer):
    raise NotImplementedError
```
