import torch

# # Generate input data
# input_data = torch.tensor([1+2j, 3-4j, 5j, 6])

# # Invoke torch.all to process input data
# result = torch.all(input_data)

# print(result)

import torch

input_data = torch.tensor([1+2j, 3-4j, 5j, 6])

result = torch.all(input_data)
print(result)

input_data = input_data.cuda()
result = torch.all(input_data)
print(result)

# https://github.com/pytorch/pytorch/issues/120875
# A complex tensor