import tensorflow as tf

# Generate input data
input_data_1 = tf.constant([[1, 2, 3], [4, 5, 6]])
input_data_2 = tf.constant([[7, 8, 9], [10, 11, 12]])

# Create a tensor list
input_handle = tf.raw_ops.TensorListReserve(element_dtype=tf.int32, element_shape=[2, 3], num_elements=2)
input_handle = tf.raw_ops.TensorListSetItem(input_handle=input_handle, index=0, item=input_data_1)
input_handle = tf.raw_ops.TensorListSetItem(input_handle=input_handle, index=1, item=input_data_2)

# Invoke TensorListConcat with explicit shape
concatenated_data, lengths = tf.raw_ops.TensorListConcat(input_handle=input_handle, element_dtype=tf.int32, element_shape=[6])

# Print the concatenated data
print(concatenated_data)

# https://github.com/tensorflow/tensorflow/issues/63722
# A 1-dimensional tensor (vector)