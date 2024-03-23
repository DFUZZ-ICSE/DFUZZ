

import os
import openai
import re
import pickle
import json



def read_output(output_path):
    output = {}
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                for idx, value in data.items():
                    output[idx] = value
    return output


def extract_code(text):
    count = 0
    modified_text = ""
    lines = text.split("\n")
    starts = []
    ends = []
    line_cnt = 0
    for line in lines:
        if line.startswith("```"):
            if count % 2 == 0:
                starts.append(line_cnt)
            else:
                ends.append(line_cnt)
            count += 1
        else:
            modified_text += line + "\n"
        
        line_cnt += 1
    
    if len(starts) == 0 and len(ends) == 0:
        msg = "There is no code block in the input text."
        return None, msg

    if len(starts) != len(ends):
        msg = "The code blocks in the input text are not conforming to the Markdown syntax."
        # print(text)
        return None, msg
    
    if len(starts) > 1:
        msg = "There are several code blocks in the input text. Please ensure that there is only one code block."
        return None, msg
    
    return "\n".join(lines[starts[0]+1:ends[0]]), ""


def read_INDEX(INDEX_PATH, output_path, seeds_path, finished_path):
    new_cnt = 0

    if os.path.exists(finished_path):
        with open(finished_path, 'rb') as f:
            finished = pickle.load(f)
    else:
        finished = []

    

    outputs = read_output(output_path)

    if not os.path.exists(seeds_path):
        os.makedirs(seeds_path)

    with open(INDEX_PATH, 'rb') as file:
        INDEX = pickle.load(file)
    # print(INDEX)

    for key, value in INDEX.items():
        if str(value) not in outputs.keys():
            continue

        if value in finished:
            # This file has been analyzed
            continue
        finished.append(value)
        

        with open(os.path.join(seeds_path, f"{value}.py"), 'w') as file:
            code, msg = extract_code(outputs[str(value)])
            if code:
                new_cnt += 1
                file.write(code)
            else:
                print(f"{key}.py")
                print(f"Error: {msg}")
    
    with open(finished_path, 'wb') as f:
        pickle.dump(finished, f)

    print("new files num:", new_cnt)
    




if __name__ == "__main__":
    output_path = "./outputs/torch/output.jsonl"
    INDEX_PATH = "./outputs/torch/INDEX.pkl"
    seeds_path = "./outputs/torch/group9" # to store the extracted programs
    finished_path = "./outputs/torch/finished.pkl"


    read_INDEX(INDEX_PATH, output_path, seeds_path, finished_path)