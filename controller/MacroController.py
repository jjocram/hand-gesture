from GestureDetector import GestureBuffer
from controller.BaseController import BaseController


class MacroController(BaseController):
    def __init__(self, macro_file_path: str, keypoint_labels_path: str, point_history_labels_path: str,
                 automata_descriptor_path: str, execute_actions: bool):
        super().__init__(keypoint_labels_path, point_history_labels_path, automata_descriptor_path, execute_actions)

        self.macro_file_path = macro_file_path

    def consume_gesture(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer):
        super(MacroController, self)._consume_gesture(static_gesture_buffer,
                                                      dynamic_gesture_buffer,
                                                      input_accepted_callback=self._write_on_file)

    def _write_on_file(self, input_gesture):
        with open(self.macro_file_path, "a+") as macro_file:
            macro_file.write(f"{input_gesture}\n")
