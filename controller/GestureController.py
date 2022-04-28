from GestureDetector import GestureBuffer
from controller.BaseController import BaseController


class GestureController(BaseController):

    def __init__(self, keypoint_labels_path: str, point_history_labels_path: str, automata_descriptor_path: str,
                 execute_actions: bool):
        super().__init__(keypoint_labels_path, point_history_labels_path, automata_descriptor_path, execute_actions)

    def consume_gesture(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer):
        super(GestureController, self)._consume_gesture(static_gesture_buffer,
                                                        dynamic_gesture_buffer,
                                                        input_accepted_callback=None)
