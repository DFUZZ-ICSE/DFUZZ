import tensorflow as tf

# Generate input data
var = tf.Variable([[1.0, 2.0], [3.0, 4.0]], dtype=tf.complex64)  # Change var to a complex tensor
accum = tf.Variable([[0.1, 0.2], [0.3, 0.4]])
lr = 0.01
grad = tf.constant([[0.1, 0.2], [0.3, 0.4]])
indices = tf.constant([0, 1])  # Make indices one-dimensional
momentum = 0.9

# Invoke tf.raw_ops.ResourceSparseApplyKerasMomentum
result = tf.raw_ops.ResourceSparseApplyKerasMomentum(var=var.handle, accum=accum.handle, lr=lr, grad=grad, indices=indices, momentum=momentum)

# Print the result
print(result)

# https://github.com/tensorflow/tensorflow/issues/63720
# A complex tensor