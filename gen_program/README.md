# Build environment
```
    conda activate icse2025
```

# Generate a valid program for each API
```
    python genPrograms.py
```

Note that you should run `monitor_mem.py` at the same time to kill the programs that occupy too much memory:
```
    python monitor_mem.py
```


# Perform mutation
## For each target API, generate prompts based on the generated valid program and generated mutator.
```
    python gen_prompts_for_mutators.py 
```

## Run the prompts
```
    python run_prompts.py 
```

Because we do not have enough API keys, we have to divide the target programs into multiple batches.
After a execution stopped, we rerun `python gen_prompts_for_mutators.py ` and `python run_prompts.py`.

If we want to extract the generated programs, we run the following cmd to extract the newest generated programs.
Before run it, you need to define the target fileflod name.
```
    python extract_res.py 
```

## test coverage based on mutated programs