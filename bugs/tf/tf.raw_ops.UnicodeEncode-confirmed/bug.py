import tensorflow as tf

# Generate input data
input_values = tf.constant([72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100])  # Unicode codepoints for "Hello World"
input_splits = tf.constant([[0, 5, 11]])  # Split indices for the input_values with two dimensions
output_encoding = "UTF-8"

# Invoke tf.raw_ops.unicode_encode
output = tf.raw_ops.UnicodeEncode(input_values=input_values, input_splits=input_splits, output_encoding=output_encoding)

# Print the output
print(output)

# https://github.com/tensorflow/tensorflow/issues/63379
# A 2D tensor on a CPU backend