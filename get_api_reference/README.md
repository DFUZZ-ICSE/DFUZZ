# Build environment
```
    conda create -n icse2025_experiment python=3.8
    conda activate icse2025_experiment
    pip install -r requirements.txt
```

We also need to fix a bug in the library astunparse in order to run TitanFuzz. To run the following commands, you need to have git installed (https://github.com/git-guides/install-git).
```
    # Remember to replace `/your/conda/path/` with your local conda path.
    # You can check with `which python` after activating the conda environment `titanfuzz`.
    cd /your/conda/path/lib/python3.8/site-packages/astunparse

    # You need to have git installed to run this command.
    git apply --whitespace=fix /share/tsinghua/inferencefuzz_experiment/inferencefuzz/gen_program_llm/unparser.patch
```

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