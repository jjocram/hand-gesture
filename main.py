import threading
from argparse import ArgumentParser
from enum import Enum, auto

import cv2

from controller.BaseController import BaseController
from controller.GestureController import GestureController
from GestureDetector import GestureDetector, GestureBuffer
from controller.MacroController import MacroController
from controller.MacroRunner import MacroRunner
from cvfpscalc import CvFpsCalc


class Mode(Enum):
    OPERATIONAL = 0
    EDIT_STATIC_GESTURE = 1
    EDIT_DYNAMIC_GESTURE = 2
    CREATE_NEW_MACRO = auto()
    RUN_MACRO = auto()


def get_args():
    parser = ArgumentParser(prog="Hand gesture recognizer")

    parser.add_argument("--interactive", action='store_true')

    return vars(parser.parse_args())


def learning_mode_get_mode_and_number():
    print("""Available datasets:
            0 - Static hand gesture
            1 - Dynamic hand gesture""")
    dataset = int(input("Which dataset do you want to edit:"))
    if dataset == 0:
        labels_path = "model/keypoint_classifier/keypoint_classifier_label.csv"
        mode = Mode.EDIT_STATIC_GESTURE
    else:
        labels_path = "model/point_history_classifier/point_history_classifier_label.csv"
        mode = Mode.EDIT_DYNAMIC_GESTURE

    with open(labels_path, 'r') as labels_file:
        labels = labels_file.readlines()

    new_or_enhance = int(input("Do you want to add a new gesture (0) or enhance an already existent one (1):"))
    if new_or_enhance == 0:
        gesture_number = len(labels)
        new_gesture_label = input("Gesture label:")
        with open(labels_path, 'a') as labels_file:
            labels_file.write(f"\n{new_gesture_label}")
    else:
        for i, label in enumerate(labels):
            print(i, "-", label)
        gesture_number = int(input("Which gesture do you want to enhance:"))

    return mode, gesture_number


def macro_mode():
    print("""What do you want to do:
    0 - Create a new macro
    1 - Run an existent one
    """)
    mode = int(input("Choose:"))
    if mode == 0:
        macro_name = input("Name of the macro:")
        return Mode.CREATE_NEW_MACRO, macro_name
    else:
        macro_file_path = input("File path:")
        return Mode.RUN_MACRO, macro_file_path


def get_mode_and_number_with_interaction():
    print("""Available modes:
    0 - Operational mode
    1 - Learning mode
    2 - Macro mode""")
    mode = int(input("Which mode do you want to use:"))

    if mode == 0:  # Operational
        # Mode = 0
        return Mode.OPERATIONAL, -1
    elif mode == 1:  # Learning
        # Mode = 1 or 2
        return learning_mode_get_mode_and_number()
    elif mode == 2:  # Macros
        # Model = 3, 4
        return macro_mode()


def save_number(key, number):
    if key == 32:
        return number
    else:
        return -1


static_gesture_buffer = GestureBuffer(buffer_len=5)
dynamic_gesture_buffer = GestureBuffer(buffer_len=5)


def control(controller: BaseController):
    global static_gesture_buffer
    global dynamic_gesture_buffer
    controller.consume_gesture(static_gesture_buffer, dynamic_gesture_buffer)


def main():
    args = get_args()

    model_keypoint_classifier_path = "model/keypoint_classifier/keypoint_classifier.tflite"
    labels_keypoint_classifier_path = "model/keypoint_classifier/keypoint_classifier_label.csv"
    model_point_history_classifier_path = "model/point_history_classifier/point_history_classifier.tflite"
    labels_point_history_classifier_path = "model/point_history_classifier/point_history_classifier_label.csv"
    automata_descriptor_path = "controller/automata_descriptor.json"

    cap_device = 0
    cap_width = 960
    cap_height = 540

    min_detection_confidence = 0.7
    min_tracking_confidence = 0.5

    saving_number = -1
    macro_file_path = ""
    options = None

    if args["interactive"]:
        mode, options = get_mode_and_number_with_interaction()
        if mode == Mode.EDIT_STATIC_GESTURE or mode == Mode.EDIT_DYNAMIC_GESTURE:
            saving_number = options
        elif mode == Mode.CREATE_NEW_MACRO:
            macro_file_path = f"macros/{options}"
        elif mode == Mode.RUN_MACRO:
            macro_file_path = options
    else:
        mode, saving_number = Mode.OPERATIONAL, -1

    cap = cv2.VideoCapture(cap_device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)

    gesture_detector = GestureDetector(min_detection_confidence,
                                       min_tracking_confidence,
                                       model_keypoint_classifier_path,
                                       labels_keypoint_classifier_path,
                                       model_point_history_classifier_path,
                                       labels_point_history_classifier_path,
                                       history_length=16)

    gesture_controller = GestureController(labels_keypoint_classifier_path,
                                           labels_point_history_classifier_path,
                                           automata_descriptor_path,
                                           execute_actions=True)
    macro_controller = MacroController(macro_file_path,
                                       labels_keypoint_classifier_path,
                                       labels_point_history_classifier_path,
                                       automata_descriptor_path,
                                       execute_actions=False)

    cv_fps_calc = CvFpsCalc(buffer_len=10)

    print("Running the Hand Gesture Recognizer with this options:")
    print(f"mode: {mode.name} ({mode.value})\noptions: {options}")

    if mode is Mode.RUN_MACRO:
        MacroRunner(options, automata_descriptor_path).run()
    else:
        while True:
            # Get fps
            fps = cv_fps_calc.get()

            # If ESC is pressed quit
            key = cv2.waitKey(10)
            if key == 27:  # ESC
                break

            number = save_number(key, saving_number)

            # Get image from the webcam
            ret, image = cap.read()
            if not ret:
                break

            # Recognize the gesture
            debug_image, static_hand_gesture_id, dynamic_hand_gesture_id = gesture_detector.recognize(image,
                                                                                                      number,
                                                                                                      mode.value,
                                                                                                      fps)
            static_gesture_buffer.add_gesture(static_hand_gesture_id)
            dynamic_gesture_buffer.add_gesture(dynamic_hand_gesture_id)

            if mode == Mode.OPERATIONAL:
                threading.Thread(target=control, args=(gesture_controller,)).start()
            elif mode == Mode.CREATE_NEW_MACRO:
                threading.Thread(target=control, args=(macro_controller,)).start()

            # Show image on the screen
            cv2.imshow('Hand Gesture Recognition', debug_image)

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
