import threading

import cv2

from GestureController import GestureController
from GestureDetector import GestureDetector, GestureBuffer
from cvfpscalc import CvFpsCalc


def select_mode(key, mode):
    number = -1
    if 48 <= key <= 57:  # 0 ~ 9
        number = key - 48
    if key == 110:  # n -> recognition
        mode = 0
    if key == 107:  # k -> New static gesture -> select a number after that
        mode = 1
    if key == 104:  # h -> New moving gesture -> select a number after thats
        mode = 2
    return number, mode


gesture_buffer = GestureBuffer(buffer_len=5)


def control(controller: GestureController):
    global gesture_buffer
    controller.gesture_control(gesture_buffer)


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
        debug_image, gesture_id = gesture_detector.recognize(image, number, mode, fps)
        gesture_buffer.add_gesture(gesture_id)

        threading.Thread(target=control, args=(gesture_controller,)).start()

        # Show image on the screen
        cv2.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
