import tensorflow as tf

# Generate input data
input_tensor = tf.zeros([15, 15, 15])
indices = tf.constant([[[0, 0, 0], [1, 1, 1]], [[2, 2, 2], [3, 3, 3]], [[4, 4, 4], [5, 5, 5]], [[6, 6, 6], [7, 7, 7]], [[8, 8, 8], [9, 9, 9]], [[10, 10, 10], [11, 11, 11]], [[12, 12, 12], [13, 13, 13]], [[14, 14, 14], [0, 0, 0]], [[1, 1, 1], [2, 2, 2]], [[3, 3, 3], [4, 4, 4]], [[5, 5, 5], [6, 6, 6]], [[7, 7, 7], [8, 8, 8]], [[9, 9, 9], [10, 10, 10]], [[11, 11, 11], [12, 12, 12]], [[13, 13, 13], [14, 14, 14]]])
updates = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0])  # Cast updates to float

# Invoke tf.tensor_scatter_nd_add
result = tf.tensor_scatter_nd_add(input_tensor, indices, updates)

# Print the result
print(result)

# https://github.com/tensorflow/tensorflow/issues/63380
# A tensor with shape (15, 15, 15) which has both a trailing dimension and total number of elements not divisible by 16