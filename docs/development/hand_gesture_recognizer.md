# Hand gesture recognizer
In the `GestureDetector.py` file there is the definition of the classes:

- `GestureDetector`: that uses MediaPipe and Tensorflow models to recognize hand gestures.
- `GestureBuffer`: that holds a sequence of gestures to use in successive steps.
## Initialization
The method `__init__(...)` initialize all the variables needed for the recognizer to work:

- Load MediaPipe
```py
self.hands = mediapipe.solutions.hands.Hands(
            static_image_mode=False,  # We will use a real time image
            max_num_hands=1,  # We will use only one hand
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
```

- Load the static gesture classifier and the dynamic gesture classifier
``` py
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
```

## Recognize
The method `recognize` take as input:

- The `image` representing the frame to analyze
- The `number` representing the ID of the gesture in case the user want to save it (*learning mode*)
- The `mode` in which the program has been launched
- The `fps` to write on image to be more informative

After the initialization of some variables used later the image is given as input to the MediaPipe model to receive in output the list of landmarks coordinate if a hand is founded in the image. If this happen, the landmarks coordinate are normalized and converted (to be compatible with the Tensorflow models) and given as input to the two classifier. The classifiers' output is written in the two buffers and the predicted gestures are returned. 
!!! info "Static and dynamic gestures"
    Each time the method is invoked it tries to recognize both a static gesture and a dynamic gesture and it returns both the predictions.

``` py
# Bounding box calculation
bounding_box_rect = calc_bounding_rect(debug_image, hand_landmarks)

# Landmark calculation
landmark_list = calc_landmark_list(debug_image, hand_landmarks)

# Conversion to relative coordinates / normalized coordinates
pre_processed_landmark_list = pre_process_landmark(landmark_list)
pre_processed_point_history_list = pre_process_point_history(debug_image, self.point_history)

# Write to dataset (1)
logging_csv(number, mode, pre_processed_landmark_list, pre_processed_point_history_list)

# Hand sign classification
static_hand_gesture_id = self.keypoint_classifier(pre_processed_landmark_list)

for i in [4, 8, 12, 16, 20]: # (2)
    self.point_history.append(landmark_list[i])

# Finger gesture classification
point_history_len = len(pre_processed_point_history_list)
if point_history_len == (self.history_length * 2 * 5):
    dynamic_hand_gesture_id = self.point_history_classifier(pre_processed_point_history_list)

# Calculate the gesture IDs in the latest calculation
self.finger_gesture_history.append(dynamic_hand_gesture_id)
most_common_dynamic_gesture = Counter(self.finger_gesture_history).most_common()

# Drawing information on the image
debug_image = draw_bounding_rect(debug_image, bounding_box_rect)
debug_image = draw_landmarks(debug_image, landmark_list)
debug_image = draw_info_text(
    debug_image,
    bounding_box_rect,
    handedness,
    self.keypoint_classifier_labels[static_hand_gesture_id],
    self.point_history_classifier_labels[most_common_dynamic_gesture[0][0]],
)
```

1. It will write only if the `mode` is `LEARING` and the `number` is not `None`
2. For the dynamic hand gestures the classifier uses the landmarks `4, 8, 12, 16, 20` that are the landmarks of the tip of the fingers.
