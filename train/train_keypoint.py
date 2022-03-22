import tensorflow as tf
from sklearn.model_selection import train_test_split

from train.utils import convert_to_tflite, train_model_with_time, \
    evaluate_model_with_time, get_callbacks, get_num_classes_from_labels_file, get_dataset, get_train_test_evaluate_datasets


def get_model(num_classes: int):
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input((21 * 2,)),
        tf.keras.layers.Dropout(0.0),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.0),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.0),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])

    return model


def train(train_name: str, sample_number: [int | None], **kwargs):
    dataset_path = "model/keypoint_classifier/keypoint.csv"
    labels_path = "model/keypoint_classifier/keypoint_classifier_label.csv"
    model_save_path = "model/keypoint_classifier/keypoint_classifier.hdf5"
    tflite_save_path = "model/keypoint_classifier/keypoint_classifier.tflite"
    log_dir = f"keypoint_tensorboard_logs/{train_name}"

    num_classes = get_num_classes_from_labels_file(labels_path)
    x_dataset, y_dataset = get_dataset(dataset_path, sample_number)

    # Train-test split
    x_train, y_train, x_test, y_test, x_evaluate, y_evaluate = get_train_test_evaluate_datasets(x_dataset,
                                                                                                y_dataset,
                                                                                                train_size=0.75,
                                                                                                evaluation_size=0.2)

    model = get_model(num_classes)

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

    convert_to_tflite(model, tflite_save_path)
