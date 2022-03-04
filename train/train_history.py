import tensorflow as tf
from numpy import loadtxt
from sklearn.model_selection import train_test_split

from train.utils import get_num_classes_from_labels_file, convert_to_tflite, train_model_with_time, \
    evaluate_model_with_time, get_callbacks


def get_model(num_classes: int, time_steps: int, dimension: int):
    # model = tf.keras.models.Sequential([
    #     tf.keras.layers.InputLayer(input_shape=(time_steps * dimension,)),
    #     tf.keras.layers.Dropout(0.2),
    #     tf.keras.layers.Dense(24, activation='relu'),
    #     tf.keras.layers.Dropout(0.5),
    #     tf.keras.layers.Dense(10, activation='relu'),
    #     tf.keras.layers.Dense(num_classes, activation='softmax')
    # ])
    model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(input_shape=(time_steps * dimension,)),
        tf.keras.layers.Reshape((time_steps, dimension), input_shape=(time_steps * dimension,)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(16, input_shape=[time_steps, dimension]),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(10, activation='relu'),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])

    return model


def train(train_name: str):
    dataset_path = "model/point_history_classifier/point_history.csv"
    labels_path = "model/point_history_classifier/point_history_classifier_label.csv"
    model_save_path = "model/point_history_classifier/point_history_classifier.hdf5"
    tflite_save_path = "model/point_history_classifier/point_history_classifier.tflite"
    log_dir = f"point_history_tensorboard_logs/{train_name}"

    num_classes = get_num_classes_from_labels_file(labels_path)
    time_steps = 16
    dimension = 2

    # Read the dataset
    x_dataset = loadtxt(dataset_path, delimiter=',', dtype='float32', usecols=list(range(1, (time_steps * dimension) + 1)))
    y_dataset = loadtxt(dataset_path, delimiter=',', dtype='int32', usecols=(0,))

    # Train-test split
    x_train, x_test, y_train, y_test = train_test_split(x_dataset, y_dataset, train_size=0.75)
    x_train, x_evaluate, y_train, y_evaluate = train_test_split(x_train, y_train, train_size=0.8)

    model = get_model(num_classes, time_steps, dimension)

    # Model compilation
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    train_model_with_time(model,
                          x_train, y_train, x_test, y_test,
                          callbacks=get_callbacks(model_save_path, log_dir),
                          batch_size=64,
                          epochs=10000)

    evaluate_model_with_time(model,
                             x_evaluate, y_evaluate,
                             batch_size=64)

    model.save(model_save_path, include_optimizer=False)
    model = tf.keras.models.load_model(model_save_path)

    convert_to_tflite(model, tflite_save_path)
