import torch

# Generate input data
input_data = torch.tensor([True, True, False, True])

# Invoke torch.all to process input data
result = torch.all(input_data)

print(result)