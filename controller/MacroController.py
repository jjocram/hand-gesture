import threading
from time import sleep

from GestureDetector import GestureBuffer
from utils import get_char


class MacroController:
    def __init__(self, macro_file_path: str):
        self.last_static = -1
        self.last_dynamic = -1
        self.sending_message = threading.Lock()

        self.state = 'q0'

        self.macro_file_path = macro_file_path

    def gesture_control(self, static_gesture_buffer: GestureBuffer, dynamic_gesture_buffer: GestureBuffer):
        with self.sending_message:
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

            # Automata management
            to_sleep = False
            with open(self.macro_file_path, 'a+') as macro_file:
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
                    print(f"Saving: picking up parcel: {letter}")
                    print("-------------------------------------")
                    macro_file.write(f"pick_up {letter}\n")

                    self.state = 'q3'
                    to_sleep = True
                elif self.state == 'q2':  # Robot waiting for "direction" without parcel
                    letter = get_char(self.last_static, self.last_dynamic)
                    print(letter)
                    print(f"Saving command: going to {letter}")
                    print("---------------------------")
                    macro_file.write(f"go_to {letter}\n")

                    self.state = 'q0'
                    to_sleep = True
                elif self.state == 'q3':  # Robot with package
                    if self.last_dynamic == 5:  # Drop down
                        print("Saving command: drop down parcel")
                        print("---------------------------------")
                        macro_file.write("drop_down\n")

                        self.state = 'q0'
                        to_sleep = True
                    elif self.last_dynamic == 3:  # Go to
                        print("Going to (with parcel):", end=" ")

                        self.state = 'q4'
                        to_sleep = True
                elif self.state == 'q4':  # Robot waiting for "direction" with parcel
                    letter = get_char(self.last_static, self.last_dynamic)
                    print(letter)
                    print(f"Saving command: going to {letter}")
                    print("---------------------------")
                    macro_file.write(f"go_to {letter}\n")

                    self.state = 'q3'
                    to_sleep = True

                if to_sleep:
                    sleep(4)