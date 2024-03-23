import torch

# Generate input data
input_data = torch.randn(3, 3)

# Invoke torch.fft.fft2 to process input data
output = torch.fft.fft2(input_data)

print(output)