import tensorflow as tf

# Generate input data
input_data = tf.constant([[1.5, 2.5, 3.5], [4.5, 5.5, 6.5]])

# Define min and max values per channel
min_per_channel = tf.constant([1.0, 2.0, 3.0])
max_per_channel = tf.constant([2.0, 3.0, 4.0])

# Invoke tf.raw_ops.FakeQuantWithMinMaxVarsPerChannel with inputs as 0-dimensional tensor and max as a 1x3 tensor
quantized_output = tf.raw_ops.FakeQuantWithMinMaxVarsPerChannel(inputs=tf.constant(0.0), min=min_per_channel, max=max_per_channel, num_bits=8, narrow_range=False)

# Print the quantized output
print(quantized_output)

# https://github.com/tensorflow/tensorflow/issues/63355
# 0-dimensional tensor