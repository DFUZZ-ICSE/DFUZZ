import tensorflow as tf

# Generate input data
input_data = tf.random.normal([1, 10, 10, 3])

# Define paddings
paddings = tf.constant([[0, 0], [1, 1], [1, 1], [0, 0]])

# Define filter
filter = tf.random.normal([3, 3, 3, 16])

# Define mode
mode = "REFLECT"  # Change mode to "REFLECT" or "SYMMETRIC"

# Define strides
strides = [1, 1, 1, 1]

# Define padding
padding = "VALID"

# Invoke tf.raw_ops.FusedPadConv2D
output = tf.raw_ops.FusedPadConv2D(input=input_data, paddings=paddings, filter=filter, mode=mode, strides=strides, padding=padding)

print(output)