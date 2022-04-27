import threading
from time import sleep

from GestureDetector import GestureBuffer
from controller.AutomataManager import AutomataManager


class GestureController:

    def __init__(self):
        self.last_static = -1
        with open("model/keypoint_classifier/keypoint_classifier_label.csv") as label_file:
            self.static_gesture_map = {i: chr(i + ord('a')) for i in range(len(label_file.readlines()))}

        self.last_dynamic = -1
        with open("model/point_history_classifier/point_history_classifier_label.csv") as label_file:
            self.dynamic_gesture_map = {i: label.lower().replace(" ", "_").replace("\n", "") for i, label in enumerate(label_file.readlines())}

        self.sending_message = threading.Lock()

        self.automata = AutomataManager("controller/automata_descriptor.json")

    def gesture_control(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer):
        with self.sending_message:
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

            # Automata management
            input_gesture = dynamic_gesture if dynamic_gesture else static_gesture
            if input_gesture and input_gesture != "static":
                input_accepted = self.automata.consume_input(input_gesture)
                if input_accepted:
                    sleep(4)