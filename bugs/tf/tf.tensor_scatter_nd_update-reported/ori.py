import tensorflow as tf

# Generate input data
input_tensor = tf.zeros([4, 4])
indices = tf.constant([[0, 0], [1, 1]])
updates = tf.constant([1, 2], dtype=tf.float32)  # Cast updates to float

# Invoke tf.tensor_scatter_nd_update
result = tf.tensor_scatter_nd_update(input_tensor, indices, updates)

# Print the result
print(result)