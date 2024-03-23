import tensorflow as tf

# Generate input data
input_data = tf.constant([0.0, 1.0, 2.0, 3.0, 4.0])

# Invoke tf.experimental.numpy.cos to process input data
result = tf.experimental.numpy.cos(input_data)

print(result)