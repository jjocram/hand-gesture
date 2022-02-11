from classifier.Classifier import Classifier


class KeyPointClassifier(Classifier):
    def __init__(self, model_path, num_threads):
        super().__init__(model_path, num_threads)

    def __call__(self, landmark_list):
        _, result_index = super(KeyPointClassifier, self).__call__(landmark_list)
        return result_index
