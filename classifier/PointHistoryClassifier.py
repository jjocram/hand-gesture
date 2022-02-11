import numpy

from classifier.Classifier import Classifier


class PointHistoryClassifier(Classifier):
    def __init__(self, model_path: str, num_threads: int, score_th: float, invalid_value: int):
        super().__init__(model_path, num_threads)

        self.score_th = score_th
        self.invalid_value = invalid_value

    def __call__(self, point_history):
        result, result_index = super(PointHistoryClassifier, self).__call__(point_history)

        if numpy.squeeze(result)[result_index] < self.score_th:
            return self.invalid_value
        else:
            return result_index
