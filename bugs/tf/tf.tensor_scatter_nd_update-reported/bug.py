import tensorflow as tf

# Generate input data
input_tensor = tf.zeros([2, 2, 2])  # A tensor that contains other tensors, creating a nested structure
indices = tf.constant([[[0, 0, 0], [1, 1, 1]], [[1, 0, 1], [0, 1, 0]]])
updates = tf.constant([1, 2], dtype=tf.float32)  # Cast updates to float

# Invoke tf.tensor_scatter_nd_update
result = tf.tensor_scatter_nd_update(input_tensor, indices, updates)

# Print the result
print(result)

# https://github.com/tensorflow/tensorflow/issues/63375
# A tensor that contains other tensors, creating a nested structure.