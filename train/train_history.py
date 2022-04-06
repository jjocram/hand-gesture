import tensorflow as tf

from train.utils import get_num_classes_from_labels_file, convert_to_tflite, train_model_with_time, \
    evaluate_model_with_time, get_callbacks, get_dataset, get_train_test_evaluate_datasets


def get_model(num_classes: int, time_steps: int, dimension: int, number_of_fingers: int):
    # model = tf.keras.models.Sequential([
    #     tf.keras.layers.InputLayer(input_shape=(time_steps * dimension * number_of_fingers,)),
    #     tf.keras.layers.Dropout(0.2),
    #     tf.keras.layers.Dense(24, activation='relu'),
    #     tf.keras.layers.Dropout(0.5),
    #     tf.keras.layers.Dense(10, activation='relu'),
    #     tf.keras.layers.Dense(num_classes, activation='softmax')
    # ])
    model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(input_shape=(time_steps * dimension * number_of_fingers,)),
        tf.keras.layers.Reshape((time_steps, dimension*number_of_fingers), input_shape=(time_steps * dimension * number_of_fingers,)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(16, input_shape=[time_steps, dimension*number_of_fingers]),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(10, activation='relu'),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])

    return model


def train(train_name: str, sample_number: int, **kwargs):
    dataset_path = "model/point_history_classifier/point_history.csv"
    labels_path = "model/point_history_classifier/point_history_classifier_label.csv"
    model_save_path = "model/point_history_classifier/point_history_classifier.hdf5"
    tflite_save_path = "model/point_history_classifier/point_history_classifier.tflite"
    log_dir = f"point_history_tensorboard_logs/{train_name}"

    num_classes = get_num_classes_from_labels_file(labels_path)
    time_steps = 16
    dimension = 2
    number_of_fingers = 5

    # Read the dataset
    y_dataset, x_dataset = get_dataset(dataset_path, sample_number)

    # Train test split
    x_train, y_train, x_test, y_test, x_evaluate, y_evaluate = get_train_test_evaluate_datasets(x_dataset,
                                                                                                y_dataset,
                                                                                                train_size=0.75,
                                                                                                evaluation_size=0.2)

    model = get_model(num_classes, time_steps, dimension, number_of_fingers)

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

    #convert_to_tflite(model, tflite_save_path)
