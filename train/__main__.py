import argparse
from .train_keypoint import train


def cli_argument_parser() -> dict:
    arguments = argparse.ArgumentParser(prog="Human-Robot in tandem Train")

    arguments.add_argument("train_model",
                           choices=["static_gesture", "moving_gesture"],
                           help="Choose which model train: static_gesture for the Keypoint Classifier, moving_gesture for the Point History Classifier")

    arguments.add_argument("--train-name",
                           type=str)

    return vars(arguments.parse_args())


if __name__ == "__main__":
    args = cli_argument_parser()
    print(args)
    if args["train_model"] == "static_gesture":
        print("Training on static hand gestures")
        train(train_name=args["train_name"])
    else:  # args["train_model"] == "moving_gesture"
        print("Training on moving hand gestures")
