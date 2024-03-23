import tensorflow as tf

# Generate input data
input_data = tf.constant([[1, 2], [3, 4], [5, 6]])
indices = tf.constant([0, 1])

# Create a resource variable on a different device and with a different dtype
with tf.device('/device:GPU:0'):
    resource_var = tf.Variable([7, 8, 9], dtype=tf.float32)

# Use tf.raw_ops.ResourceGather to gather values
output = tf.raw_ops.ResourceGather(resource=resource_var.handle, indices=indices, dtype=tf.int32)

print(output)

# known bug
# tensor_1 is on a different device than the input device and has a different dtype