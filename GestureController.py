import threading
from time import sleep

from GestureDetector import GestureBuffer


class GestureController:

    def __init__(self):
        self.last_static = -1
        self.last_dynamic = -1
        self.sending_message = threading.Lock()

        self.state = 'q0'

    def gesture_control(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer):
        with self.sending_message:
            static_gesture_id = static_gesture_buffer.get_gesture()
            dynamic_gesture_id = dynamic_gesture_buffer.get_gesture()

            if static_gesture_id is not None and static_gesture_id != -1:
                if self.last_static != static_gesture_id:
                    print("Static gesture id:", static_gesture_id)
                    self.last_static = static_gesture_id

            if dynamic_gesture_id is not None and dynamic_gesture_buffer != -1:
                if self.last_dynamic != dynamic_gesture_id:
                    print("Dynamic gesture id:", dynamic_gesture_id)
                    self.last_static = dynamic_gesture_id

            # Automata management
            if self.state == 'q0':
                pass
            elif self.state == 'q1':
                pass
            elif self.state == 'q2':
                pass
            elif self.state == 'q3':
                pass
            elif self.state == 'q4':
                pass

            sleep(2)
