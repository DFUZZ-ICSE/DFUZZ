import tensorflow as tf
import numpy as np

# Generate random input data
matrix = np.random.rand(2, 3)
rhs = np.random.rand(3)

# Invoke tf.linalg.solve
result = tf.linalg.solve(matrix, rhs)

# Print the result
print(result)

# https://github.com/tensorflow/tensorflow/issues/63339
# A 1-dimensional tensor (vector)