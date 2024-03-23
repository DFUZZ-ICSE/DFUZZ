import tensorflow as tf
import numpy as np

# Generate input data
batch_size = 1
image_height = 100
image_width = 100
num_channels = 3
num_boxes = 2

images = np.random.rand(batch_size, image_height, image_width, num_channels)
boxes = np.random.rand(batch_size, num_boxes, 4)
colors = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])  # Define colors for the bounding boxes

# Invoke tf.image.draw_bounding_boxes
input_images = tf.convert_to_tensor(images, dtype=tf.float32)
input_boxes = tf.convert_to_tensor(boxes, dtype=tf.float32)
input_colors = tf.convert_to_tensor(colors, dtype=tf.float32)

output_images = tf.image.draw_bounding_boxes(input_images, input_boxes, colors)

# Print the output images
print(output_images)