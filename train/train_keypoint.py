import tensorflow as tf
from numpy import loadtxt
from sklearn.model_selection import train_test_split

from train.utils import get_num_classes_from_labels_file, take_time, convert_to_tflite


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

def get_callbacks():
    return []

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


def train(train_name: str):
    dataset_path = "model/keypoint_classifier/keypoint.csv"
    labels_path = "model/keypoint_classifier/keypoint_classifier_label.csv"
    model_save_path = "model/keypoint_classifier/keypoint_classifier.hdf5"
    tflite_save_path = "model/keypoint_classifier/keypoint_classifier.tflite"
    log_dir = f"keypoint_tensorboard_logs/{train_name}"

    num_classes = get_num_classes_from_labels_file(labels_path)

    # Read the dataset
    X_dataset = loadtxt(dataset_path, delimiter=',', dtype='float32', usecols=list(range(1, (21 * 2) + 1)))
    Y_dataset = loadtxt(dataset_path, delimiter=',', dtype='int32', usecols=(0,))

    # Train-test split
    X_train, X_test, Y_train, Y_test = train_test_split(X_dataset, Y_dataset, train_size=0.75)
    X_train, X_evaluate, Y_train, Y_evaluate = train_test_split(X_train, Y_train, train_size=0.8)

    model = get_model(num_classes)

    # Model compilation
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Model checkpoint callback
    cp_callback = tf.keras.callbacks.ModelCheckpoint(model_save_path, verbose=1, save_weights_only=False,
                                                     save_best_only=True)

    # Callback for early stopping
    es_callback = tf.keras.callbacks.EarlyStopping(patience=50, verbose=1)

    # Callback for save tensorboard data
    tb_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    train_model_with_time(model,
                          X_train, Y_train, X_test, Y_test,
                          callbacks=[cp_callback, es_callback, tb_callback],
                          batch_size=64,
                          epochs=10000)

    evaluate_model_with_time(model,
                             X_evaluate, Y_evaluate,
                             batch_size=64)

    convert_to_tflite(model, tflite_save_path)

