import torch

# Generate input data
input_data = torch.randn(3, 3, dtype=torch.complex64)

# Create a sparse output tensor
output = torch.sparse_coo_tensor(input_data.shape, dtype=torch.complex64)

# Invoke torch.conj_physical to process input data and store the result in the sparse output tensor
torch.conj_physical(input_data, out=output)

# Print the output
print(output)

# https://github.com/pytorch/pytorch/issues/120989
# mutator: A sparse tensor