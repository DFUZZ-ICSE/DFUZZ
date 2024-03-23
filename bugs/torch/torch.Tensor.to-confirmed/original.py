import torch

# Generate input data
input_data = torch.randn(3, 3)

# Process input data using torch.Tensor.to
processed_data = input_data.to(torch.double)

print(processed_data)
