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


@take_time("Keypoint fit")
def train_model_with_time(model, x_train, y_train, x_test, y_test, callbacks, batch_size, epochs):
    # Model train
    model.fit(
        x_train,
        y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(x_test, y_test),
        callbacks=callbacks
    )


@take_time("Keypoint evaluate")
def evaluate_model_with_time(model, x_evaluate, y_evaluate, batch_size):
    # Model evaluation
    val_loss, val_acc = model.evaluate(x_evaluate, y_evaluate, batch_size=batch_size)

    print("Validation loss:", val_loss, "\nValidation accuracy:", val_acc)


def get_callbacks(model_save_path: str, log_dir: str):
    # Model checkpoint callback
    cp_callback = tf.keras.callbacks.ModelCheckpoint(model_save_path, verbose=1, save_weights_only=False,
                                                     save_best_only=True)

    # Callback for early stopping
    es_callback = tf.keras.callbacks.EarlyStopping(patience=50, verbose=1)

    # Callback for save tensorboard data
    tb_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    return [cp_callback, es_callback, tb_callback]
