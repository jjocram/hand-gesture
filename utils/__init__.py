import copy
import csv
import itertools

import cv2 as cv
import numpy as np


def get_char(static_gesture_id, dynamic_gesture_id):
    if dynamic_gesture_id == 0 or dynamic_gesture_id == 1:
        return chr(dynamic_gesture_id + ord('a'))
    else:
        return chr(static_gesture_id + ord('a'))

def _draw_text_white_on_black(img, text, position):
    cv.putText(img=img,
               text=text,
               org=position,
               fontFace=cv.FONT_HERSHEY_SIMPLEX,
               fontScale=1.0,
               color=(0, 0, 0),
               thickness=4,
               lineType=cv.LINE_AA)

    cv.putText(img=img,
               text=text,
               org=position,
               fontFace=cv.FONT_HERSHEY_SIMPLEX,
               fontScale=1.0,
               color=(255, 255, 255),
               thickness=2,
               lineType=cv.LINE_AA)


def _draw_text(img, text, position, color):
    cv.putText(img=img,
               text=text,
               org=position,
               fontFace=cv.FONT_HERSHEY_SIMPLEX,
               fontScale=0.6,
               color=color,
               thickness=1,
               lineType=cv.LINE_AA)


def calc_bounding_rect(image, landmarks):
    """

    :param image:
    :param landmarks:
    :return:
    """
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)

    return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks):
    """

    :param image:
    :param landmarks:
    :return:
    """
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoints
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


def pre_process_landmark(landmark_list):
    """

    :param landmark_list:
    :return:
    """
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Converto to one-dimension list
    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list


def pre_process_point_history(image, point_history):
    image_width, image_height = image.shape[1], image.shape[0]

    temp_point_history = copy.deepcopy(point_history)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, point in enumerate(temp_point_history):
        if index == 0:
            base_x, base_y = point[0], point[1]

        temp_point_history[index][0] = (temp_point_history[index][0] -
                                        base_x) / image_width
        temp_point_history[index][1] = (temp_point_history[index][1] -
                                        base_y) / image_height

    # Convert to one-dimension list
    temp_point_history = list(itertools.chain.from_iterable(temp_point_history))

    return temp_point_history


def logging_csv(number, mode, landmark_list, point_history_list):
    """
    Save data on csv
    :param number: the identification number of the gesture (referees to label file)
    :param mode: the current application mode: 0=recognition; 1=create new static gesture; 2=create new moving gesture
    :param landmark_list: used with mode 1, the landmarks to add to the csv
    :param point_history_list: used with mode 2, the point history to add to the csv
    """
    if mode == 0:
        return
    if mode == 1 and (number >= 0):
        csv_path = 'model/keypoint_classifier/keypoint.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    if mode == 2 and (number >= 0):
        csv_path = 'model/point_history_classifier/point_history.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *point_history_list])


def draw_landmarks(image, landmark_point):
    """
    Draws landmarks and the connecting lines between them
    :param image:
    :param landmark_point:
    :return:
    """

    black_rgb = (0, 0, 0)
    white_rgb = (255, 255, 255)

    def line_between_landmarks(points: list):
        """
        Given a list of points draw the lines between them
        :param points: a list of integers
        """
        for first, second in zip(points[:-1], points[1:]):
            cv.line(image, tuple(landmark_point[first]), tuple(landmark_point[second]), black_rgb, 6)
            cv.line(image, tuple(landmark_point[first]), tuple(landmark_point[second]), white_rgb, 2)

    def draw_key_points(landmark_coordinate, is_fingertip=False):
        """
        Given a landmark draw a circle on the image centered in the landmark position
        :param landmark_coordinate: a tuple (X, Y), the center of the landmark
        :param is_fingertip: fingertips have a bigger circle
        """
        radius = 8 if is_fingertip else 5
        cv.circle(image, (landmark_coordinate[0], landmark_coordinate[1]), radius, black_rgb, -1)
        cv.circle(image, (landmark_coordinate[0], landmark_coordinate[1]), radius, white_rgb, 1)

    if len(landmark_point) > 0:
        # Thumb
        line_between_landmarks([2, 3, 4])

        # Index finger
        line_between_landmarks([5, 6, 7, 8])

        # Middle finger
        line_between_landmarks([9, 10, 11, 12])

        # Ring finger
        line_between_landmarks([13, 14, 15, 16])

        # Little finger
        line_between_landmarks([17, 18, 19, 20])

        # Palm
        line_between_landmarks([0, 1, 2, 5, 9, 13, 17, 0])

    # Keyppoints
    for index, landmark in enumerate(landmark_point):
        if index in (4, 8, 12, 16, 20):
            draw_key_points(landmark, is_fingertip=True)
        else:
            draw_key_points(landmark, is_fingertip=False)

    return image


def draw_bounding_rect(image, brect):
    """
    Draws the rectangle around the hand
    :param image: the image where to draw the
    :param brect: the bounding box of the rectangle to draw
    :return: the image with the bounding box drawn on top of it
    """
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]), (0, 0, 0), 1)

    return image


def draw_info_text(image, brect, handedness, hand_sign_text, finger_gesture_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22), (0, 0, 0), -1)

    info_text = handedness.classification[0].label[0:]
    if hand_sign_text != "":
        info_text = info_text + ':' + hand_sign_text

    _draw_text(image, info_text, (brect[0] + 5, brect[1] - 4), (255, 255, 255))

    if finger_gesture_text != "":
        _draw_text_white_on_black(image, f"Finger gesture: {finger_gesture_text}", (10, 60))

    return image


def draw_point_history(image, point_history):
    """
    Draws a circle for each point in point history. It shows the moving gestures
    :param image: the image where to draw the points
    :param point_history: the list of points to draw
    :return: the image with the points drawn on top of it
    """
    color_rgb = (152, 251, 152)
    for index, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:  # If X and Y are not zeros
            cv.circle(img=image,
                      center=(point[0], point[1]),
                      radius=1 + (int(index / 2) % 5),
                      color=color_rgb,
                      thickness=2)

    return image


def draw_info(image, fps, mode, number):
    """
    Draws some information on the image
    :param image: the image where to draw the infos
    :param fps: Frames Per Seconds
    :param mode: the current mode of the application
    :param number: the number where the gesture is being saved
    :return: the image with the infos drawn on top of it
    """

    # Draws the FPS number white on a black background (this is way two text are written)
    _draw_text_white_on_black(image, f"FPS: {str(fps)}", (10, 30))

    mode_string = ['Logging Key Point', 'Logging Point History']
    if 1 <= mode <= 2:
        _draw_text(image, f"MODE: {mode_string[mode - 1]}", (10, 90), (255, 255, 255))

        if 0 <= number <= 9:
            _draw_text(image, f"NUM: {str(number)}", (10, 110), (255, 255, 255))

    return image
