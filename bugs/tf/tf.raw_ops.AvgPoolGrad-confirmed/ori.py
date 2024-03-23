import tensorflow as tf

# Generate input data
input_data = tf.random.normal([1, 28, 28, 3])
grad = tf.random.normal([1, 14, 14, 3])

# Perform average pooling
result = tf.nn.avg_pool2d(input_data, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID', data_format='NHWC')

# Compute gradient
grad_result = tf.raw_ops.AvgPoolGrad(orig_input_shape=tf.shape(input_data), grad=grad, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID', data_format='NHWC')

print(grad_result)