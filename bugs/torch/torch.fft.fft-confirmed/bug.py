import torch

indices = torch.LongTensor([[0, 1, 2],
                            [2, 0, 1]])
values = torch.FloatTensor([3, 4, 5])
# indices = indices.cuda()
# values = values.cuda()
input_data = torch.sparse_coo_tensor(indices, values, [2, 3])
output = torch.fft.fft(input_data.to_dense())
print(output)

indices = torch.LongTensor([[0, 1, 2],
                            [2, 0, 1]])
values = torch.FloatTensor([3, 4, 5])
indices = indices.cuda()
values = values.cuda()
input_data = torch.sparse_coo_tensor(indices, values, [2, 3])
output = torch.fft.fft(input_data.to_dense())

print(output)

# # Generate input data
# indices = torch.LongTensor([[0, 1, 2],
#                             [2, 0, 1]])
# values = torch.FloatTensor([3, 4, 5])
# input_data = torch.sparse_coo_tensor(indices, values, [2, 3])

# # Invoke torch.fft.fft to process input data
# output = torch.fft.fft(input_data.to_dense())

# print(output)

# https://github.com/pytorch/pytorch/issues/120902
# A sparse tensor