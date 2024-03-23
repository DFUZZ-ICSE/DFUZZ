import tensorflow as tf

# Generate input data
input_data = tf.constant([0.0, 1.0, 2.0, 3.0, 4.0])


with tf.device('cpu:0'):
    quantized_input_data = tf.quantization.fake_quant_with_min_max_args(input_data, min=-6.0, max=6.0)
    print(quantized_input_data)

with tf.device('gpu:0'):
    quantized_input_data = tf.quantization.fake_quant_with_min_max_args(input_data, min=-6.0, max=6.0)
    print(quantized_input_data)


# # Invoke tf.experimental.numpy.cos to process quantized input data
# result = tf.experimental.numpy.cos(quantized_input_data)
# print(result)

# https://github.com/tensorflow/tensorflow/issues/63271
# A tensor that is already quantized