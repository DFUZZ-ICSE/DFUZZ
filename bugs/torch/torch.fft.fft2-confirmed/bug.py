import torch

# Generate input data
input_data = torch.randn(3, 3)

# Invoke torch.fft.fft2 to process input data with an empty list for the dim parameter
output = torch.fft.fft2(input_data, dim=[])

print(output)

# https://github.com/pytorch/pytorch/issues/120986
# mutator: An empty tensor