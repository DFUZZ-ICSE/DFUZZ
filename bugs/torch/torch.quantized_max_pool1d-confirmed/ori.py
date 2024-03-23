import torch

# Generate input data
input_data = torch.randn(1, 3, 10).float()  # Change the data type to float

# Quantize the input data
scale = 1.0
zero_point = 0
input_data_quantized = torch.quantize_per_tensor(input_data, scale, zero_point, torch.quint8)

# Invoke torch.quantized_max_pool1d
output = torch.quantized_max_pool1d(input_data_quantized, kernel_size=[2])

print(output)