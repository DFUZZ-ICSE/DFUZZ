import torch
import numpy as np

# Generate random input data
input_data = torch.randn(3, 4, 5, 6)

# Define scale, zero_point, axis, quant_min, and quant_max
scale = np.array([0.1, 0.2, 0.3, 0.4])  # Convert scale to a numpy array
zero_point = torch.tensor([1, 2, 3, 4], dtype=torch.int32)  # Ensure the dtype is torch.int32
axis = 1
quant_min = 0
quant_max = 255

# Invoke torch.fake_quantize_per_channel_affine
output = torch.fake_quantize_per_channel_affine(input_data, torch.from_numpy(scale), zero_point, axis, quant_min, quant_max)

print(output)

# https://github.com/pytorch/pytorch/issues/120903
# tensor_1 is a numpy array, not a tensor