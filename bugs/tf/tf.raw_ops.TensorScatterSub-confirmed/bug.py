import tensorflow as tf

# Generate input data
tensor = tf.constant([1, 2, 3, 4, 5])
indices = tf.constant([[[1], [3]], [[0], [2]]])  # Nested structure for indices
updates = tf.constant([10, 20])

# Invoke tf.raw_ops.TensorScatterSub
result = tf.raw_ops.TensorScatterSub(tensor=tensor, indices=indices, updates=updates)

# Print the result
print(result)

# https://github.com/tensorflow/tensorflow/issues/63378
# A tensor that contains other tensors, creating a nested structure.