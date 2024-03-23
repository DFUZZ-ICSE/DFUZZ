import torch

input_data = torch.tensor([float('nan')])
different_input = input_data.to(dtype=torch.int32)
print(different_input)

input_data = torch.tensor([float('nan')]).cuda()
different_input = input_data.to(dtype=torch.int32)
print(different_input)

# import torch
# input_data = torch.tensor([float('nan')])
# different_input = input_data.to(dtype=torch.int32)
# print(different_input)

# https://github.com/pytorch/pytorch/issues/121226
# a string tensor