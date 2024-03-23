# Collect the information of APIs
## Get the reference of Pytorch
```
    conda activate icse2025_experiment
    python get_reference_torch.py
```
Then you will get two files: `api_description.json` and `apis_info.json`. 
The `api_description.json` records the description for all target APIs.
The `apis_info.json` records the variables's name and type for all target APIs.

## Get the reference of TensorFlow
```
    conda activate tensorflow
    python get_reference_tf.py
```
