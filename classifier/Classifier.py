import numpy
import tensorflow


class Classifier:
    def __init__(self, model_path: str, num_threads: int):
        self.interpreter = tensorflow.lite.Interpreter(model_path=model_path, num_threads=num_threads)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def __call__(self, data):
        input_details_tensor_index = self.input_details[0]["index"]
        self.interpreter.set_tensor(tensor_index=input_details_tensor_index,
                                    value=numpy.array([data], dtype=numpy.float32))
        self.interpreter.invoke()

        output_details_tensor_index = self.output_details[0]['index']

        result = self.interpreter.get_tensor(tensor_index=output_details_tensor_index)

        result_index = numpy.argmax(numpy.squeeze(result))

        return result, result_index
