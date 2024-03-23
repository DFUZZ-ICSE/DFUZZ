import tensorflow as tf

# Generate input data
var = tf.Variable([1.0, 2.0, 3.0])
accum = tf.Variable([0.1, 0.2, 0.3])
lr = 0.01
l1 = 0.1
l2 = 0.01
grad = tf.constant([0.1, 0.2, 0.3])

# Convert var and accum to resource tensors
var_resource = tf.raw_ops.VarHandleOp(dtype=var.dtype, shape=var.shape)
accum_resource = tf.raw_ops.VarHandleOp(dtype=accum.dtype, shape=accum.shape)

# Assign var and accum to the resource tensors
assign_var = tf.raw_ops.AssignVariableOp(resource=var_resource, value=var)
assign_accum = tf.raw_ops.AssignVariableOp(resource=accum_resource, value=accum)

# Invoke tf.raw_ops.ResourceApplyProximalAdagrad with resource tensors
result = tf.raw_ops.ResourceApplyProximalAdagrad(var=var_resource, accum=accum_resource, lr=lr, l1=l1, l2=l2, grad=grad)

# Print the result
print(result)