import tensorflow as tf
import numpy as np

# Generate input data
batch_size = 1
image_height = 100
image_width = 100
num_channels = 3
num_boxes = 2

images = np.random.rand(batch_size, image_height, image_width, num_channels).astype(np.float32)
boxes = np.random.rand(batch_size, num_boxes, 4).astype(np.float32)

# Invoke tf.raw_ops.DrawBoundingBoxes
drawn_images = tf.raw_ops.DrawBoundingBoxes(images=tf.convert_to_tensor(images),
                                           boxes=tf.convert_to_tensor(boxes))

# Print the result
print(drawn_images)