from datetime import datetime

from tensorboard.data.experimental import ExperimentFromDev
import tensorflow as tf
from numpy import ndarray
from pandas import concat, read_csv
from sklearn.model_selection import train_test_split

ExperimentFromDev()

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


def get_callbacks(model_save_path: str, log_dir: str) -> list:
    """
    Get the callbacks to use during the training phase
    :param model_save_path: Where save the model
    :param log_dir: tensorboard directory
    :return: a list of callbacks: ModelCheckpoint, EarlyStopper, TensorboardLogger
    """
    # Model checkpoint callback
    cp_callback = tf.keras.callbacks.ModelCheckpoint(model_save_path, verbose=1, save_weights_only=False,
                                                     save_best_only=True)

    # Callback for early stopping
    es_callback = tf.keras.callbacks.EarlyStopping(patience=50, verbose=1)

    # Callback for save tensorboard data
    tb_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    return [es_callback, tb_callback]
    # return [cp_callback, es_callback, tb_callback]


def get_dataset(dataset_path: str, sample_number: [int | None]) -> tuple[ndarray, ndarray]:
    """
    Construct the x_dataset and the y_dataset starting from a csv file
    :param dataset_path: path of the dataset built with this tool
    :param labels_path: path of the labels to use
    :param sample_number: number of samples per class. None if you want to use the whole dataset
    :return: the y_dataset and the x_dataset to use to train the network
    """
    df = read_csv(dataset_path, header=None)
    classes = df[0].unique()

    # Downsampling
    if sample_number:
        print("Undersampling...")
        reduced_dfs = [df[df[0] == i].sample(sample_number, random_state=42) for i in classes]
        df = concat(reduced_dfs).sample(frac=1).reset_index(drop=True)

    return df[0].to_numpy(dtype='int32'), df.drop(df.columns[[0]], axis=1).to_numpy(dtype='float32')


def get_train_test_evaluate_datasets(x_dataset: ndarray, y_dataset: ndarray, train_size: float, evaluation_size: float) -> tuple[ndarray, ndarray, ndarray, ndarray, ndarray, ndarray]:
    """
    Split the dataset in three parts: train, test and evaluate
    :param x_dataset: the whole x_dataset
    :param y_dataset: the whole y_dataset
    :param train_size: the size of the train dataset, 1-train_size will be the size of the test_dataset
    :param evaluation_size: from the train_dataset reduced by train_size, it will be reduced again reserving evaluation_size for the evaluation dataset
    :return: the following datasets: x_train, y_train, x_test, y_test, x_evaluate, y_evaluate
    """
    x_train, x_test, y_train, y_test = train_test_split(x_dataset, y_dataset, train_size=train_size)
    x_train, x_evaluate, y_train, y_evaluate = train_test_split(x_train, y_train, train_size=1 - evaluation_size)

    return x_train, y_train, x_test, y_test, x_evaluate, y_evaluate
