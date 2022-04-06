import threading
from time import sleep

from GestureDetector import GestureBuffer
from controller.AutomataManager import AutomataManager
from utils import get_letter_gesture_id


class GestureController:

    def __init__(self):
        self.last_static = -1
        with open("model/keypoint_classifier/keypoint_classifier_label.csv") as label_file:
            self.static_gesture_map = {i: chr(i + ord('a')) for i in range(len(label_file.readlines()))}

        self.last_dynamic = -1
        with open("model/point_history_classifier/point_history_classifier_label.csv") as label_file:
            self.dynamic_gesture_map = {i: label.lower().replace(" ", "_").replace("\n", "") for i, label in enumerate(label_file.readlines())}

        self.sending_message = threading.Lock()

        self.navigator = None

        self.automata = AutomataManager("controller/automata_descriptor.json", self.navigator)

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

            """
            to_sleep = False
            if self.state == 'q0':  # Robot without package
                if self.last_dynamic == 3:  # Go to
                    print("Going to (without parcel):", end=" ")

                    self.state = 'q2'
                    to_sleep = True
                elif self.last_dynamic == 4:  # Pick up
                    print("Picking up:", end=" ")

                    self.state = 'q1'
                    to_sleep = True
            elif self.state == 'q1':  # Robot waiting for parcel id
                letter = get_char(self.last_static, self.last_dynamic)
                print(letter)
                print(f"Sending command: picking up parcel: {letter}")
                print("-------------------------------------")

                self.state = 'q3'
                to_sleep = True
            elif self.state == 'q2':  # Robot waiting for "direction" without parcel
                letter = get_char(self.last_static, self.last_dynamic)
                print(letter)
                print(f"Sending command: going to {letter}")
                print("---------------------------")

                self.state = 'q0'
                to_sleep = True
            elif self.state == 'q3':  # Robot with package
                if self.last_dynamic == 5:  # Drop down
                    print("Sending command: drop down parcel")
                    print("---------------------------------")

                    self.state = 'q0'
                    to_sleep = True
                elif self.last_dynamic == 3:  # Go to
                    print("Going to (with parcel):", end=" ")

                    self.state = 'q4'
                    to_sleep = True
            elif self.state == 'q4':  # Robot waiting for "direction" with parcel
                letter = get_char(self.last_static, self.last_dynamic)
                print(letter)
                print(f"Sending command: going to {letter}")
                print("---------------------------")

                self.state = 'q3'
                to_sleep = True

            if to_sleep:
                sleep(4)
            """
