import tensorflow as tf

# Generate input data
input_data = tf.data.Dataset.range(10).map(lambda x: tf.strings.as_string(x))

# Invoke tf.raw_ops.ExperimentalDatasetToTFRecord to process input data
filename = tf.constant("output.tfrecord")
compression_type = tf.constant("GZIP")
tf.raw_ops.ExperimentalDatasetToTFRecord(input_dataset=input_data._variant_tensor, filename=filename, compression_type=compression_type)