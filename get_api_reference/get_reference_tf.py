import openai
import json
import tensorflow as tf
import io
import sys
import random
import copy
import time
import os
from tqdm import tqdm


def get_api_inference(file_path):

    target_apis = []
    with open(file_path, 'r') as file:
        for line in file:
            target_apis.append(line.strip())

    # Dictionary to store API information
    captured_infos = {}

    # Redirect the standard output to capture the help output
    help_output = io.StringIO()
    sys.stdout = help_output

    # Call the help function on each API and capture the output
    invalid_num = 0
    invalid_set = []
    for api in target_apis:
        # Reset the StringIO object
        help_output.truncate(0)
        help_output.seek(0)
        
        # Call help and capture output
        valid = 1
        try:
            help(eval(api))
        except Exception as e:
            valid = 0
            print(e)
        
        # Get the captured help output as a string
        captured_info = help_output.getvalue()
        
        # Store the captured API information
        if valid:
            captured_infos[api] = captured_info
        else:
            invalid_num += 1
            invalid_set.append(api)
            captured_infos[api] = "none"

    # Reset the standard output
    sys.stdout = sys.__stdout__

    # Close the StringIO object
    help_output.close()


    # Now, captured_infos contains the API information as strings, with keys being the API names.
    # for api_name, info in captured_infos.items():
    #     print("-", api_name)
    #     info = info.split('\n')
    #     print('\n'.join(info[:10]))

    #     print("\n")

    # print("invalid_num:", invalid_num)
    # print("invalid_set:", invalid_set)

    return captured_infos

def request_openai_api(messages, max_retries = 20, temperature = 0, model = "GPT-3.5"):

    if model == "GPT-3.5":
        model = "gpt-3.5-turbo-1106"

        with open('./config.json', 'r') as file:
            data = json.load(file)
        api_keys = data['api_keys']

    elif model == "GPT-4":
        # model = "gpt-4-0125-preview"
        model = "gpt-4-1106-preview"

        with open('./config-gpt-4-1106-preview.json', 'r') as file:
            data = json.load(file)
        api_keys = data['api_keys']
        api_base = data['api_base']

        openai.api_base = api_base
    else:
        print("Invalid Model")

    

    start_time = time.time()

    # for key in api_keys:
    attempts = 0
    completion = None
    while attempts < max_retries:
        key = random.choice(api_keys)
        # print("key:", key)
        try:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                api_key=key,
                request_timeout=120
            )
            break
        except Exception as e:
            attempts += 1
            print(e)

            if "deactivated" in str(e):
              data['api_keys'].remove(key)
              with open('./config.json', 'w') as json_file:
                json.dump(data, json_file)

            if attempts == max_retries:
                time.sleep(60)
                attempts = 0

    end_time = time.time()
    request_time = end_time - start_time
    # print("---- request time cost:", request_time)

    if not completion:
        return None

    output = completion['choices'][0]['message']['content'].strip()
    return output


messages_template = [
    {"role": "system", "content": "You are a LLM."},
    {"role": "user", "content": ""}
]

prompt_template = """
The information of <TARGET_API>: 
```
<INFO>
```

Extract the types of input parameters for <TARGET_API>. Considering only the following variable types: {Tensor, Int, Bool, Str, Float, Scalar, List}.
Output the results in the following format:
[
    {
        "variable name":"",
        "variable type":"" # Only consider the following variable types: {Tensor, Int, Bool, Str, Float, Scalar, List}. If the variable type is not one of these target types, it is represented as "unknown".
    }
]

Directly output the JSON content without any additional output (e.g., no need for code delimiters like ```).
"""



def extract_code(text):
    try:
        dataset = json.loads(text)
        var_to_type = {}
        for data in dataset:
            var_name = data["variable name"]
            var_type = data["variable type"]
            var_to_type[var_name] = var_type

            type_valid = 0
            for tmp in ["tensor", "int", "bool", "str", "float", "scalar", "list", "unknown"]:
                if tmp in var_type.lower():
                    type_valid = 1
                    break

            if type_valid == 0:
                msg = var_type + " is not considered -> Considering only the following variable types: {Tensor, Int, Bool, Str, Float, Scalar, List}. Otherwise, return 'unknown'."
                return None, msg

            # if var_type.lower() not in ["tensor", "int", "bool", "str", "float", "scalar", "list", "unknown"]:
            #     msg = var_type + " is not considered -> Considering only the following variable types: {Tensor, Int, Bool, Str, Float, Scalar, List}. Otherwise, return 'unknown'."
            #     return None, msg

        return var_to_type, ""
            
    except Exception as e:
        msg = "Directly output the JSON content without any additional output (e.g., no need for code delimiters like ```)."
        return None, msg

def reask(dialog, extract_code, MAX_TRY):
    SUCCESS = 0
    try_cnt = 0
    while try_cnt < MAX_TRY:
        # print("\ntry_cnt:", try_cnt)
        print(dialog)
        # raw_llm = request_openai_api(dialog, 20, model = "GPT-4")
        raw_llm = request_openai_api(dialog, 90)
        print("raw_llm:", raw_llm)

        code, msg = extract_code(raw_llm) 
        print("code:", code)
        print("msg:", msg)

        if code:
            SUCCESS = 1
            break
        else:
            dialog.append(
                {"role": "assistant", "content": raw_llm}
            )
            dialog.append(
                {"role": "user", "content": msg + " Please generate again."}
            )
            print(msg)

        try_cnt += 1

    
    if SUCCESS:
        return code, 1
    else:
        print("---- Can not finish this task. Here are the unsloved problem:", msg)
        return None, 0

def analysis(api_name, description):
    # construct prompt

    prompt = prompt_template.replace("<TARGET_API>", api_name)
    prompt = prompt.replace("<INFO>", description)

    print("\n--- prompt start ---")
    print(prompt)
    print("--- prompt end ---\n")

    messages = copy.deepcopy(messages_template)
    messages[-1]["content"] = prompt

    # ask LLM
    res, valid = reask(messages, extract_code, 3)
    if valid:
        return res
    else:
        return None

file_path = "./data/tf_valid_apis.txt"  # the path of the target api list
api_description_path = "./results/tensorflow/api_description.json" # the path of api_description
res_path = "./results/tensorflow/apis_info.json" # the path of apis_info

apis_info = {}
if os.path.exists(res_path):
    with open(res_path, 'r') as json_file:
        apis_info = json.load(json_file)

        # for ori, res in decompose_res.items():
        #     print("ori:", ori)
        #     print("res:", res, "\n")
else:
    apis_info = {}

if os.path.exists(api_description_path):
    print("api_description has been extracted")
    with open(api_description_path, 'r') as json_file:
        captured_infos = json.load(json_file)
else:
    captured_infos = get_api_inference(file_path)

    with open(api_description_path, 'w') as json_file:
        json.dump(captured_infos, json_file)


for api_name, info in tqdm(captured_infos.items(), desc="Processing", unit="item"):
    if api_name in apis_info.keys():
        print(api_name, "has been analyzed")
        continue

    print("\n\n==========", api_name, "==========")
    info = info.split('\n')
    info = '\n'.join(info[:10])

    var_to_type = analysis(api_name, info)
    if var_to_type:
        apis_info[api_name] = var_to_type

    with open(res_path, 'w') as json_file:
        json.dump(apis_info, json_file)