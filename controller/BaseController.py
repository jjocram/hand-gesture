import threading

from GestureDetector import GestureBuffer


class BaseController:
    def __init__(self):
        self.last_static = -1
        self.last_dynamic = -1

        self.lock = threading.Lock()

    def _get_gesture(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer):
        static_gesture_id = static_gesture_buffer.get_gesture()
        dynamic_gesture_id = dynamic_gesture_buffer.get_gesture()

        if static_gesture_id is not None and static_gesture_id != -1:
            if self.last_static != static_gesture_id:
                # print("Static gesture id:", static_gesture_id)
                self.last_static = static_gesture_id

        if dynamic_gesture_id is not None and dynamic_gesture_buffer != -1:
            if self.last_dynamic != dynamic_gesture_id:
                # print("Dynamic gesture id:", dynamic_gesture_id)
                self.last_dynamic = dynamic_gesture_id

    def consume_gesture(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer):
        raise NotImplementedError
