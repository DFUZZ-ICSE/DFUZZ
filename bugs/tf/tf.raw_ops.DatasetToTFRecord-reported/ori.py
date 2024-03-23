import tensorflow as tf

# Generate input data
input_data = [1, 2, 3, 4, 5]

# Convert input data to strings
input_data_strings = [str(d) for d in input_data]

# Create a dataset from the input data strings
dataset = tf.data.Dataset.from_tensor_slices(input_data_strings)

# Define the filename for the TFRecord file
filename = "output.tfrecord"

# Invoke tf.raw_ops.DatasetToTFRecord to process input data
tf.raw_ops.DatasetToTFRecord(input_dataset=dataset._variant_tensor, filename=filename, compression_type="")