import copy
import csv
from collections import deque, Counter

import cv2
import mediapipe

from classifier.KeypointClassifier import KeyPointClassifier
from classifier.PointHistoryClassifier import PointHistoryClassifier
from utils import calc_bounding_rect, calc_landmark_list, pre_process_landmark, pre_process_point_history, logging_csv, \
    draw_bounding_rect, draw_landmarks, draw_info_text, draw_point_history, draw_info


class GestureDetector:

    def __init__(self,
                 min_detection_confidence: float,
                 min_tracking_confidence: float,
                 model_keypoint_classifier_path: str,
                 labels_keypoint_classifier_path: str,
                 model_point_history_classifier_path: str,
                 labels_point_history_classifier_path: str,
                 history_length: int):
        """
        Initialize the hand gesture detector
        :param min_detection_confidence:
        :param min_tracking_confidence:
        :param model_keypoint_classifier_path:
        :param labels_keypoint_classifier_path:
        :param model_point_history_classifier_path:
        :param labels_point_history_classifier_path:
        :param history_length:
        """
        # Load MediaPipe's hand tracking
        self.hands = mediapipe.solutions.hands.Hands(
            static_image_mode=False,  # We will use a real time image
            max_num_hands=1,  # We will use only one hand
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        # Load models (KeyPoint and PointHistory)
        self.keypoint_classifier = KeyPointClassifier(model_path=model_keypoint_classifier_path,
                                                      num_threads=1)
        with open(labels_keypoint_classifier_path, encoding='utf-8-sig') as labels_file:
            self.keypoint_classifier_labels = [row[0] for row in csv.reader(labels_file)]

        self.point_history_classifier = PointHistoryClassifier(model_path=model_point_history_classifier_path,
                                                               num_threads=1,
                                                               score_th=0.5,
                                                               invalid_value=0)
        with open(labels_point_history_classifier_path, encoding='utf-8-sig') as labels_file:
            self.point_history_classifier_labels = [row[0] for row in csv.reader(labels_file)]

        # Finger gesture history
        self.history_length = history_length
        self.point_history = deque(maxlen=history_length)
        self.finger_gesture_history = deque(maxlen=history_length)

    def recognize(self, image, number, mode, fps):
        # Variable for holding the gesture id
        gesture_id = -1

        # Mirror display
        image = cv2.flip(image, 1)

        # A deep copy of the image
        debug_image = copy.deepcopy(image)

        # Detection implementation
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.hands.process(image)  # MediaPipe work --> landmark recognition
        image.flags.writeable = True

        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):

                # Bounding box calculation
                bounding_box_rect = calc_bounding_rect(debug_image, hand_landmarks)

                # Landmark calculation
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                # Conversion to relative coordinates / normalized coordinates
                pre_processed_landmark_list = pre_process_landmark(landmark_list)
                pre_processed_point_history_list = pre_process_point_history(debug_image, self.point_history)

                # Write to dataset
                logging_csv(number, mode, pre_processed_landmark_list, pre_processed_point_history_list)

                # Hand sign classification
                hand_sign_id = self.keypoint_classifier(pre_processed_landmark_list)
                if hand_sign_id == 2:  # Point gesture
                    self.point_history.append(landmark_list[8])  # 人差指座標
                else:
                    self.point_history.append([0, 0])

                # Finger gesture classification
                finger_gesture_id = 0
                point_history_len = len(pre_processed_point_history_list)
                if point_history_len == (self.history_length * 2):
                    finger_gesture_id = self.point_history_classifier(pre_processed_point_history_list)

                # Calculate the gesture IDs in the latest calculation
                self.finger_gesture_history.append(finger_gesture_id)
                most_common_fg_id = Counter(self.finger_gesture_history).most_common()

                # Drawing information on the image
                debug_image = draw_bounding_rect(debug_image, bounding_box_rect)
                debug_image = draw_landmarks(debug_image, landmark_list)
                debug_image = draw_info_text(
                    debug_image,
                    bounding_box_rect,
                    handedness,
                    self.keypoint_classifier_labels[hand_sign_id],
                    self.point_history_classifier_labels[most_common_fg_id[0][0]],
                )

                gesture_id = hand_sign_id
        else:
            self.point_history.append([0, 0])

        debug_image = draw_point_history(debug_image, self.point_history)
        debug_image = draw_info(debug_image, fps, mode, number)

        return debug_image, gesture_id


class GestureBuffer:
    def __init__(self, buffer_len=10):
        self.buffer_len = buffer_len
        self._buffer = deque(maxlen=buffer_len)

    def add_gesture(self, gesture_id):
        self._buffer.append(gesture_id)

    def get_gesture(self):
        counter = Counter(self._buffer).most_common()
        if counter[0][1] >= (self.buffer_len - 1):
            self._buffer.clear()
            return counter[0][0]
        else:
            return
