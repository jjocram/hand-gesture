import threading

import cv2

from GestureController import GestureController
from GestureDetector import GestureDetector, GestureBuffer
from cvfpscalc import CvFpsCalc


def select_mode(key, mode):
    """

    :param key: the key pressed by the user, -1 if none
    :param mode: the current mode, to update or leave not changed
    :return: return the pair number  and mode
    """

    starting_letter = ord("a")
    ending_letter = ord("z")

    key_mode_recognition = ord("0")
    key_mode_new_static_gesture = ord("1")
    key_mode_new_dynamic_gesture = ord("2")

    number = -1
    if starting_letter <= key <= ending_letter:  # a ~ z
        number = key - starting_letter  # convert from 0 to 25
    if key == key_mode_recognition:  # 0 -> recognition
        mode = 0
    if key == key_mode_new_static_gesture:  # 1 -> New static gesture -> select a number after that
        mode = 1
    if key == key_mode_new_dynamic_gesture:  # 2 -> New moving gesture -> select a number after that
        mode = 2
    return number, mode


static_gesture_buffer = GestureBuffer(buffer_len=5)
dynamic_gesture_buffer = GestureBuffer(buffer_len=5)


def control(controller: GestureController):
    global static_gesture_buffer
    global dynamic_gesture_buffer
    controller.gesture_control(static_gesture_buffer, dynamic_gesture_buffer)


def main():
    cap_device = 0
    cap_width = 960
    cap_height = 540

    min_detection_confidence = 0.7
    min_tracking_confidence = 0.5

    cap = cv2.VideoCapture(cap_device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)

    gesture_detector = GestureDetector(min_detection_confidence,
                                       min_tracking_confidence,
                                       model_keypoint_classifier_path="model/keypoint_classifier/keypoint_classifier.tflite",
                                       labels_keypoint_classifier_path="model/keypoint_classifier/keypoint_classifier_label.csv",
                                       model_point_history_classifier_path="model/point_history_classifier/point_history_classifier.tflite",
                                       labels_point_history_classifier_path="model/point_history_classifier/point_history_classifier_label.csv",
                                       history_length=16)

    gesture_controller = GestureController()

    cv_fps_calc = CvFpsCalc(buffer_len=10)

    mode = 0

    while True:
        # Get fps
        fps = cv_fps_calc.get()

        # If ESC is pressed quit
        key = cv2.waitKey(10)
        if key == 27:  # ESC
            break

        number, mode = select_mode(key, mode)

        # Get image from the webcam
        ret, image = cap.read()
        if not ret:
            break

        # Recognize the gesture
        debug_image, static_hand_gesture_id, dynamic_hand_gesture_id = gesture_detector.recognize(image, number, mode, fps)
        static_gesture_buffer.add_gesture(static_hand_gesture_id)
        dynamic_gesture_buffer.add_gesture(dynamic_hand_gesture_id)

        threading.Thread(target=control, args=(gesture_controller,)).start()

        # Show image on the screen
        cv2.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
