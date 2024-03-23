import tensorflow as tf

# Generate input data
input_data = tf.constant([[1, 2, 3], [4, 5, 6]])

# Define the function to be called
@tf.function
def my_function(inputs):
    return tf.reduce_sum(inputs, axis=1)

# Create a callable from the function
callable_function = tf.function(my_function).get_concrete_function(tf.TensorSpec(shape=None, dtype=tf.int32))

# Invoke tf.raw_ops.StatefulPartitionedCall to process input data
output = tf.raw_ops.StatefulPartitionedCall(args=[input_data], Tout=None, f=callable_function)

# Print the output
print(output)

# https://github.com/tensorflow/tensorflow/issues/63721
# tensor_1 is an undefined or None value