import torch

# Generate input data
LU_data = torch.randn(3, 3)
LU_pivots = torch.empty(0, dtype=torch.int32)

# Invoke torch.lu_unpack
P, L, U = torch.lu_unpack(LU_data, LU_pivots)

# Print the results
print("P matrix:")
print(P)
print("L matrix:")
print(L)
print("U matrix:")
print(U)

# https://github.com/pytorch/pytorch/issues/121584
# An empty tensor