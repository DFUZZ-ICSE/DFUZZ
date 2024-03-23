import tensorflow as tf

# Generate input data
var = tf.Variable([1.0, 2.0, 3.0])
accum = tf.Variable([0.1, 0.2, 0.3], dtype=tf.complex64)  # Change the dtype to complex
lr = 0.01
grad = tf.constant([0.1, 0.2, 0.3])
momentum = 0.9

# Invoke tf.raw_ops.ResourceApplyMomentum with correct input types
output = tf.raw_ops.ResourceApplyMomentum(var=var.handle, accum=accum.handle, lr=lr, grad=grad, momentum=momentum)

# Print the output
print(output)

# https://github.com/tensorflow/tensorflow/issues/63696
# A complex tensor