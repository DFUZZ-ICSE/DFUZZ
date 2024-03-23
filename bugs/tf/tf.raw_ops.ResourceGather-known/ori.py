import tensorflow as tf

# Generate input data
input_data = tf.constant([[1, 2], [3, 4], [5, 6]])
indices = tf.constant([0, 1])

# Use tf.gather to gather values
output = tf.gather(input_data, indices)

print(output)