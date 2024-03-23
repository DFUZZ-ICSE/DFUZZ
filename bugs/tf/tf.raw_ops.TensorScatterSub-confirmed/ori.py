import tensorflow as tf

# Generate input data
tensor = tf.constant([1, 2, 3, 4, 5])
indices = tf.constant([[1], [3]])  # Reshape indices to match the updates shape
updates = tf.constant([10, 20])

# Invoke tf.raw_ops.TensorScatterSub
result = tf.raw_ops.TensorScatterSub(tensor=tensor, indices=indices, updates=updates)

# Print the result
print(result)