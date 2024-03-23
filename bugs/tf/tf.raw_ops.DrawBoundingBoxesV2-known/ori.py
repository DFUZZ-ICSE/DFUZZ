import tensorflow as tf
import numpy as np

# Generate input data
batch_size = 1
image_height = 100
image_width = 100
num_channels = 3
num_boxes = 2

images = tf.random.uniform((batch_size, image_height, image_width, num_channels))
boxes = tf.random.uniform((batch_size, num_boxes, 4))
colors = tf.constant([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])  # Define colors for each bounding box

# Invoke tf.raw_ops.DrawBoundingBoxesV2
output_images = tf.raw_ops.DrawBoundingBoxesV2(images=images, boxes=boxes, colors=colors)

# Print the output images
print(output_images)