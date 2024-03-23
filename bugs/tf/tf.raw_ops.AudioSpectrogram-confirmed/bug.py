import tensorflow as tf

# Generate input data
input_data = tf.random.normal([1, 44100], dtype=tf.float32)

# Invoke tf.raw_ops.AudioSpectrogram with a negative window_size
spectrogram = tf.raw_ops.AudioSpectrogram(input=input_data, window_size=-1024, stride=64, magnitude_squared=False)

# Print the spectrogram
print(spectrogram)

# https://github.com/tensorflow/tensorflow/issues/63352
# int_1 is a negative integer