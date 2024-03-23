import tensorflow as tf

# Generate input data
input_data = tf.constant([1.5, 2.5, 3.5, 4.5])

# Define input_min, input_max, num_bits, and other parameters
input_min = tf.constant(0.0)
input_max = tf.constant(5.0)
num_bits = tf.constant(8)
signed_input = True
range_given = True
narrow_range = False
axis = -1

# Invoke tf.raw_ops.QuantizeAndDequantizeV3
output_data = tf.raw_ops.QuantizeAndDequantizeV3(input=input_data, input_min=input_min, input_max=input_max, num_bits=num_bits, signed_input=signed_input, range_given=range_given, narrow_range=narrow_range, axis=axis)

# Print the output data
print(output_data)