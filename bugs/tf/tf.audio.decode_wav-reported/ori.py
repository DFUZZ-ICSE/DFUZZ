import tensorflow as tf
import numpy as np
import io

# Generate input data
sample_rate = 44100
num_channels = 2
duration_seconds = 5
num_samples = sample_rate * duration_seconds
input_data = np.random.randint(-32768, 32767, size=(num_samples, num_channels)).astype(np.int16)

# Convert NumPy array to WAV file contents
wav_io = io.BytesIO()
wav_write = tf.audio.encode_wav(input_data, sample_rate)
wav_io.write(wav_write.numpy())
wav_contents = wav_io.getvalue()

# Decode the WAV file contents
decoded_audio = tf.audio.decode_wav(wav_contents, desired_channels=2)

# Print the decoded audio tensor
print(decoded_audio)