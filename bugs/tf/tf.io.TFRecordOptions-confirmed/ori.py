import tensorflow as tf

# Generate input data
input_data = b'input_data_example'

# Create TFRecordOptions
options = tf.io.TFRecordOptions(compression_type='ZLIB')

# Process input data using TFRecordOptions
with tf.io.TFRecordWriter('output.tfrecord', options=options) as writer:
    writer.write(input_data)