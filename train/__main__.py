import argparse
from .train_keypoint import train as train_static_gestures
from .train_history import train as train_dynamic_gestures


def cli_argument_parser() -> dict:
    arguments = argparse.ArgumentParser(prog="Human-Robot in tandem Train")

    arguments.add_argument("train_model",
                           choices=["static_gesture", "dynamic_gesture"],
                           help="Choose which model train: static_gesture for the Keypoint Classifier,\
                           dynamic_gesture for the Point History Classifier.")

    arguments.add_argument("--train-name",
                           type=str)

    arguments.add_argument("--sample-number",
                           type=int,
                           required=False,
                           help="The number of elements to pick for each class downsampling the dataset.\
                           This operation is done before the train_test_split operation.\
                           If a class hasn't enough samples then, the minimum is taken between all the other classes.\
                           If this parameter is not set then, the whole dataset is used.")

    return vars(arguments.parse_args())


if __name__ == "__main__":
    args = cli_argument_parser()
    print(args)
    if args["train_model"] == "static_gesture":
        print("Training on static hand gestures")
        train_static_gestures(**args)
    else:  # args["train_model"] == "dynamic_gesture"
        train_dynamic_gestures(**args)
        print("Training on dynamic hand gestures")
