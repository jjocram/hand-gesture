import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

from sys import argv, exit

try:
    train_name = argv[1]
except IndexError:
    print("Missing argument: name of the train")
    exit(1)

dataset_path = "model/keypoint_classifier/keypoint.csv"
labels_path = "model/keypoint_classifier/keypoint_classifier_label.csv"
model_save_path = "model/keypoint_classifier/keypoint_classifier.hdf5"
tflite_save_path = "model/keypoint_classifier/keypoint_classifier.tflite"
log_dir = f"keypoint_tensorboard_logs/{train_name}"


with open(labels_path, "r") as labels_file:
    labels = [label.replace("\n", "").replace('"', '') for label in labels_file.readlines()]
    print(labels)
    NUM_CLASSES = len(labels)

# Read the dataset
X_dataset = np.loadtxt(dataset_path, delimiter=',', dtype='float32', usecols=list(range(1, (21 * 2) + 1)))
Y_dataset = np.loadtxt(dataset_path, delimiter=',', dtype='int32', usecols=(0,))

# Train-test split
X_train, X_test, Y_train, Y_test = train_test_split(X_dataset, Y_dataset, train_size=0.75)

# Classes count
counts = np.unique(Y_dataset, return_counts=True)
print("Labels found: ", counts)

# Plot the classes
"""
df = pd.DataFrame(counts)
df.T.plot(kind="bar", stacked=True)
"""

model = tf.keras.models.Sequential([
    tf.keras.layers.Input((21 * 2,)),
    tf.keras.layers.Dropout(0.0),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.0),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.0),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
])

# Model checkpoint callback
cp_callback = tf.keras.callbacks.ModelCheckpoint(model_save_path, verbose=1, save_weights_only=False, save_best_only=True)

# Callback for early stopping
es_callback = tf.keras.callbacks.EarlyStopping(patience=50, verbose=1)

# Callback for save tensorboard data
tb_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

# Model compilation
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Model train
model.fit(
    X_train,
    Y_train,
    epochs=1000,
    batch_size=64,
    validation_data=(X_test, Y_test),
    callbacks=[cp_callback, es_callback, tb_callback]
)

# Model evaluation
val_loss, val_acc = model.evaluate(X_test, Y_test, batch_size=64)

print("Validation loss:", val_loss, "\nValidation accuracy:", val_acc)

# Conversion to tflite

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_quantized_model = converter.convert()
open(tflite_save_path, 'wb').write(tflite_quantized_model)
