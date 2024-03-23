import tensorflow as tf

# Generate input data
var = tf.Variable([[1.0, 2.0], [3.0, 4.0]])
accum = tf.Variable([[0.1, 0.2], [0.3, 0.4]])
lr = 0.01
grad = tf.constant([[0.1, 0.2], [0.3, 0.4]])
indices = tf.constant([0, 1])  # Make indices one-dimensional
momentum = 0.9

# Invoke tf.raw_ops.ResourceSparseApplyKerasMomentum
result = tf.raw_ops.ResourceSparseApplyKerasMomentum(var=var.handle, accum=accum.handle, lr=lr, grad=grad, indices=indices, momentum=momentum)

# Print the result
print(result)