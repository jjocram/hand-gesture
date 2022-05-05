# Development
If you want to contribute to the project or understand how does it work you can start from here.

## Main
The starting point of the program is the `main.py` file. In this file the initial interaction with the user is handled.

```py
class Mode(Enum):
    OPERATIONAL = 0
    EDIT_STATIC_GESTURE = 1
    EDIT_DYNAMIC_GESTURE = 2
    CREATE_NEW_MACRO = auto()
    RUN_MACRO = auto()
```

The *enum* `Mode` is used to to keep track of the mode selected by the user. `OPERATIONAL`, `EDIT_STATIC_GESTURE`, and `EDIT_DYNAMIC_GESTURE` are fixed to *0, 1, 2* for retro-compatibility.

### Interactive mode
When the user pass the argument `--interactive` the program will ask some questions to the user. The methods that handle this are:
- get_mode_and_number_with_interaction
- learning_mode_get_mode_and_number
- macro_mode

### Main function
#### Configurations
First of all, the main function initialized some variables:

- Files 
    - `model_keypoint_classifier_path`: path to the `.tflite` file for the static hand gesture recognizer
    - `labels_keypoint_classifier_path`: path to the `.csv` file with the labels of the static hand gesture recognizer
    - `model_point_history_classifier_path`: path to the `.tflite` file for the dynamic hand gesture recognizer
    - `labels_point_history_classifier_path`: path to the `.csv` file with the labels of the dynamic hand gesture recognizer
    - `automata_descriptor_path`: path to the `.json` file used to describe the automaton

- OpenCV configuration
    - `cap_device`: id of the capture device
    - `cap_width`
    - `cap_height`

- MediaPipe configuration
    - `min_detection_confidence`
    - `min_tracking_confidence`

Then the `GestureController` and the `MacroController` are created.

#### Run macro
If the mode is `RUN_MACRO` then, the `run` method of the `MacroRunner` is invoked.
```py
if mode is Mode.RUN_MACRO:
    MacroRunner(options, automata_descriptor_path).run()
```

#### Hand gesture recognizer
Otherwise while `ESC` is not pressed the webcam is used to recognize both static and dynamic hand gesture. They are appended to two global buffers:
```py
debug_image, static_hand_gesture_id, dynamic_hand_gesture_id = gesture_detector.recognize(image,
                                                                                          number,
                                                                                          mode.value,
                                                                                          fps)
static_gesture_buffer.add_gesture(static_hand_gesture_id)
dynamic_gesture_buffer.add_gesture(dynamic_hand_gesture_id)
```

Then based on the selected mode the `gesture_controller` or the `macro_controller` are executed on a different thread (this has been made to avoid stuttering on the webcam view)

```py
if mode == Mode.OPERATIONAL:
    threading.Thread(target=control, args=(gesture_controller,)).start()
elif mode == Mode.CREATE_NEW_MACRO:
    threading.Thread(target=control, args=(macro_controller,)).start()
```
