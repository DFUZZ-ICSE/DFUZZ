# extract the check requirements from source codes
```
python analyze_torch.py
```
Then, we will get a `all_mutators.json` file. 
The log file is located at `logs/analyze_torch.log`.

# transfer the check requirements to mutators
```
python cluster.py
```
Then, we will get a `all_clusters.json` file which records the cluster results of all mutators.
The log file is located at `logs/cluster.log`.

```
python torch_mutator_infer.py
```
Then, we will get a `unique_mutators.json` which records the generated mutators.
The log file is located at `logs/torch_mutator_infer.log`.
