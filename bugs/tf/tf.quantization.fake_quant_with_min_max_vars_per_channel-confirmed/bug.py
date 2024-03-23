import tensorflow as tf

# Generate input data
input_data = tf.constant(3.0)

# Define min and max values per channel
min_per_channel = tf.constant(2.0)
max_per_channel = tf.constant(4.0)

# Invoke fake_quant_with_min_max_vars_per_channel
quantized_data = tf.quantization.fake_quant_with_min_max_vars_per_channel(input_data, min_per_channel, max_per_channel)

# Print the quantized data
print(quantized_data)

# https://github.com/tensorflow/tensorflow/issues/63351
# A zero-dimensional tensor (scalar)