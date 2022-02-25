from datetime import datetime

import tensorflow as tf


def get_num_classes_from_labels_file(file_path: str) -> int:
    with open(file_path, "r") as labels_file:
        labels = [label.replace("\n", "").replace('"', '') for label in labels_file.readlines()]
        print("Labels: ", labels)
        num_classes = len(labels)

    return num_classes


def take_time(name: str):
    def decorator(function):
        def inner(*args, **kwargs):
            start = datetime.now()
            function_result = function(*args, **kwargs)
            end = datetime.now()
            print(f"Function {name} took {end - start} to execute")
            return function_result

        return inner
    return decorator


def convert_to_tflite(model: str, tflite_file_path):
    # Conversion to tflite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_quantized_model = converter.convert()

    with open(tflite_file_path, 'wb') as tflite_file:
        tflite_file.write(tflite_quantized_model)
