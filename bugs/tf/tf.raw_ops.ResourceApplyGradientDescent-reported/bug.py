import tensorflow as tf

# Generate input data
var = tf.Variable(3.0 + 1j, dtype=tf.complex64)  # Change the dtype to complex
alpha = tf.constant(0.1, dtype=tf.float32)
delta = tf.constant(0.5, dtype=tf.float32)

# Invoke tf.raw_ops.ResourceApplyGradientDescent
result = tf.raw_ops.ResourceApplyGradientDescent(var=var.handle, alpha=alpha, delta=delta)

# Print the result
print(result)

# https://github.com/tensorflow/tensorflow/issues/63695
# A complex tensor