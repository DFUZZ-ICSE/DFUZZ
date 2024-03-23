import tensorflow as tf

# Generate input data
input_data = b'input_data_example'

# Create TFRecordOptions with custom compression_strategy
options = tf.io.TFRecordOptions(compression_type='ZLIB', compression_strategy=-2)

# Process input data using TFRecordOptions
with tf.io.TFRecordWriter('output.tfrecord', options=options) as writer:
    writer.write(input_data)

# https://github.com/tensorflow/tensorflow/issues/63337
# int 