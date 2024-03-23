import tensorflow as tf
import numpy as np

# Generate input data
image_height = 100
image_width = 100
num_channels = 3
num_boxes = 2

images = tf.random.uniform((image_height, image_width, num_channels))  # Change the shape to satisfy the requirement of a zero-dimensional tensor
boxes = tf.random.uniform((1, num_boxes, 4))
colors = tf.constant([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])  # Define colors for each bounding box

# Invoke tf.raw_ops.DrawBoundingBoxesV2
output_images = tf.raw_ops.DrawBoundingBoxesV2(images=images, boxes=boxes, colors=colors)

# Print the output images
print(output_images)

# https://github.com/tensorflow/tensorflow/issues/63354