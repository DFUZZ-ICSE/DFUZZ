import torch

# Generate input data
input_data = torch.randn(3, 3)
condition = torch.rand(3, 3) > 0.5
other_data = torch.ones(3, 3)

# Create a zero-dimensional tensor for the output
output = torch.tensor(0)

# Process input data using torch.where
output = torch.where(condition, input_data, other_data, out=output)

print("Input Data:")
print(input_data)
print("\nCondition:")
print(condition)
print("\nOther Data:")
print(other_data)
print("\nOutput Data:")
print(output)

# https://github.com/pytorch/pytorch/issues/121397
# A zero-dimensional tensor (scalar)