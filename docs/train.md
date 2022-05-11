---
hide:
  - navigation
---
# Train the networks
## Use the `train` package to create new `tflite` files
The `train` package has been implemented to let to everyone train their own networks based on their own dataset.

You can launch the train with the command
```bash
python3 -m train <static_gesture|dynamic_gesture> --train-name TRAIN_NAME [--sample-number N]
```

- With `static_gesture` you will train on the dataset of the static gestures. With `dynamic_gesture` you will train on the dataset of the dynamic gesture.

- `--train-name TRAIN_NAME` set the name of the train as `TRAIN_NAME`. It will be used as name for TensorBoard.

- `--sample-number N` is an optional argument. If it is passed, the size of the dataset will be `N * num_classes`

## Create a new gesture or increase the samples in the dataset of an existing one
1. Launch the application in `iteractive` mode:
  ```bash
  python3 main.py --interactive
  ```
2. Choose `1 - Learing mode`: write `1` and press `enter`
3. Choose on which dataset you want to operate: `0` for static, `1` for dynamic
4. Choose if you want create a new gesture (`0`) or enhance an already existent one (`1`)
  - If you choose to create a new gesture then, you will be asked for the name of the gesture
  - If you choose to enhance and already existent one then, you will be asked for the id of the gesture to enhance
5. The program will start and you can press the `space bar` to write on the dataset a snapshot of the position of your hand
