import torch

# Generate input data
n = 10
input_data = torch.randn(n)

# Invoke torch.fft.rfftfreq with specified parameters
out = torch.empty(2, 2, requires_grad=True)
freq = torch.fft.rfftfreq(n, out=out)

print(freq)

# https://github.com/pytorch/pytorch/issues/120988
# An empty tensor