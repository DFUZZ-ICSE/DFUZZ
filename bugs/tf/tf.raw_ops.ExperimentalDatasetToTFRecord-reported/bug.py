import tensorflow as tf

# Generate input data
input_data = tf.data.Dataset.range(10).map(lambda x: tf.strings.as_string(x))
input_data = input_data.batch(2)  # Batch the dataset to have 3 dimensions with each dimension size greater than 1

# Invoke tf.raw_ops.ExperimentalDatasetToTFRecord to process input data
filename = tf.constant("output.tfrecord")
compression_type = tf.constant("GZIP")
tf.raw_ops.ExperimentalDatasetToTFRecord(input_dataset=input_data._variant_tensor, filename=filename, compression_type=compression_type)

# https://github.com/tensorflow/tensorflow/issues/63691
# A tensor with 3 dimensions, each dimension of size greater than 1