import tensorflow as tf
import numpy as np

# Generate random input data
matrix = np.random.rand(3, 3)
rhs = np.random.rand(3, 2)

# Invoke tf.linalg.solve
result = tf.linalg.solve(matrix, rhs)

# Print the result
print(result)