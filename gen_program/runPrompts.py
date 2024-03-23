from openai_parallel_toolkit import ParallelToolkit
import time

if __name__ == '__main__':
  T1 = time.time()
  ParallelToolkit(config_path="./config.json",
                   input_path="./outputs/torch/Prompts.jsonl",
                   output_path="./outputs/torch/output.jsonl", threads = 20).run()

  T2 = time.time()
  print("Time:", T2-T1)