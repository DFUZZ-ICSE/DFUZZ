import torch

# Generate input data
n = 10
input_data = torch.randn(n)

# Invoke torch.fft.rfftfreq
freq = torch.fft.rfftfreq(n)

print(freq)