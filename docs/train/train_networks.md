# Train static and dynamic hand gesture
The process to train the two networks is similar. It only differs in the topology of the network.

The model is built with the function `get_model`. 

The `train` function calls some other functions to read the dataset in the right way:

- `get_num_classes_from_labels_file(labels_path)`
- `get_dataset(dataset_path, sample_number)`
- `get_train_test_evaluate_datasets(x_dataset, y_dataset, train_size=0.75, evaluation_size=0.2)`

Then, with two functions that take also the time the model is trained and evaluated:

- `train_model_with_time(model, x_train, y_train, x_test, y_test, callbacks=get_callbacks(model_save_path, log_dir), batch_size=64, epochs=10000)`
- `evaluate_model_with_time(model, x_evaluate, y_evaluate, batch_size=64)`

Finally, the model is converted to `tflite` with another function:

- `convert_to_tflite(model, tflite_save_path)`

## Get the dataset
### Get the number of classes from labels file
```py
def get_num_classes_from_labels_file(file_path: str) -> int:
    with open(file_path, "r") as labels_file:
        labels = [label.replace("\n", "").replace('"', '') for label in labels_file.readlines()]
        print("Labels: ", labels)
        num_classes = len(labels)

    return num_classes
```

### Read the dataset
This function read the dataset but, if a value is passed as `sample_number`, then only a random subset with `sample_number` elements for each class is taken
```py
def get_dataset(dataset_path: str, sample_number: [int | None]) -> tuple[ndarray, ndarray]:
    df = read_csv(dataset_path, header=None)
    classes = df[0].unique()

    # Downsampling
    if sample_number:
        print("Undersampling...")
        reduced_dfs = [df[df[0] == i].sample(sample_number, random_state=42) for i in classes]
        df = concat(reduced_dfs).sample(frac=1).reset_index(drop=True)

    return df[0].to_numpy(dtype='int32'), df.drop(df.columns[[0]], axis=1).to_numpy(dtype='float32')
```

### Split the dataset
Uses the `train_test_split` function of `sklearn` to randomly split the dataset
```py
def get_train_test_evaluate_datasets(x_dataset: ndarray, y_dataset: ndarray, train_size: float, evaluation_size: float) -> tuple[ndarray, ndarray, ndarray, ndarray, ndarray, ndarray]:
    x_train, x_test, y_train, y_test = train_test_split(x_dataset, y_dataset, train_size=train_size)
    x_train, x_evaluate, y_train, y_evaluate = train_test_split(x_train, y_train, train_size=1 - evaluation_size)

    return x_train, y_train, x_test, y_test, x_evaluate, y_evaluate
```

## Train and evaluate with time
A decorator is used to take time of the `fit` and `evaluate` functions
```py
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
```

```py
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
```

### Callbacks
The callbacks are got with the function `get_callbacks`

## Convert to `tflite`
```py
def convert_to_tflite(model: str, tflite_file_path):
    # Conversion to tflite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_quantized_model = converter.convert()

    with open(tflite_file_path, 'wb') as tflite_file:
        tflite_file.write(tflite_quantized_model)
```
