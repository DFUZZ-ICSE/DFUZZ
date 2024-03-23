import tensorflow as tf

# Generate input data
input_data = tf.random.normal([1, 28, 28, 3])
filter_data = tf.random.normal([3, 3, 3])
out_backprop_data = tf.random.normal([1, 28, 28, 3, 3])  # Adding an extra dimension

# Invoke tf.raw_ops.Dilation2DBackpropFilter
output = tf.raw_ops.Dilation2DBackpropFilter(input=input_data, filter=filter_data, out_backprop=out_backprop_data, strides=[1, 1, 1, 1], rates=[1, 1, 1, 1], padding="SAME")

print(output)

# known
# shape