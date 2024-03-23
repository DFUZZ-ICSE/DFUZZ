import os
import pickle
import networkx as nx
import random
import json
import copy


mutation_prompt_template = """
1. The initial program that invoke `<API>`:
```
<INIT_PROGRAM>
```

2. The information of `<API>`:
```
<API_INFO>
```

Mutate the initial program to generate a program satisfy that following requirements: 
<MUTATORS>

Please use Markdown syntax to represent code blocks. Please ensure that there is only one code block.

"""

# mutator_template = """(<N>) the parameter `<VAR>` in `<API>` satisfies the requirement of "<REQUIREMENT>". """
mutator_template = """The parameter `<VAR>` in `<API>` satisfies the requirement of "<REQUIREMENT>". """

prompt_template = """Write a program to generate input data and invoke <API_NAME> to process input data. Please use Markdown syntax to represent code blocks. Please ensure that there is only one code block.

Here are some information of this api:
```
<API_INFO>
```"""

prompt_template_without_info = """Write a program to generate input data and invoke <API_NAME> to process input data. Please use Markdown syntax to represent code blocks. Please ensure that there is only one code block."""

system = "You are an advanced Language Model assistant that can generate, execute, and evaluate code. Please use Markdown syntax to represent code blocks."

def gen_prompt(api_name, api_info):
  if api_info:
    prompt = prompt_template.replace("API_NAME", api_name)
    prompt = prompt.replace("<API_INFO>", api_info)
  else:
    prompt = prompt_template_without_info.replace("API_NAME", api_name)
  return prompt


def read_output(output_path):
  output = {} 
  finished = []
  if os.path.exists(output_path):
    with open(output_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            for idx, value in data.items():
                # print(idx, value)
                if idx not in output:
                    output[idx] = value
  
  for idx, value in output.items():
    if output[idx] != None:
      finished.append(idx)
  
  return finished


'''
  Logic generation
'''
def get_logic_lin(api_dict, outputs):
  prompt_path = os.path.join(outputs, "Prompts.jsonl")
  output_path = os.path.join(outputs, "output.jsonl")
  INDEX_path = os.path.join(outputs, "INDEX.pkl")

  allData = []
  INDEX = {}
  cnt = 0
  for api_name, api_info in api_dict.items():
    INDEX[api_name] = cnt
    prompt = gen_prompt(api_name, api_info)
    allData.append({"index":cnt, "instruction":system, "input":prompt})
    cnt += 1

  # 逐行写入 JSONL 文件
  with open(prompt_path, 'w') as file:
    for item in allData:
        json.dump(item, file)
        file.write('\n')

  with open(INDEX_path, "wb") as file:
    pickle.dump(INDEX, file)


def continue_analysis(outputs):
  prompt_path = os.path.join(outputs, "Prompts.jsonl")
  output_path = os.path.join(outputs, "output.jsonl")

  finished = read_output(output_path)

  target_prompt = []
  with open(prompt_path, 'r') as json_file:
      for line in json_file:
          json_object = json.loads(line)

          if str(json_object["index"]) not in finished:
             target_prompt.append(json_object)
  
  with open(prompt_path, 'w') as file:
    for item in target_prompt:
        json.dump(item, file)
        file.write('\n')

def add_suffix_to_type(s, types):
    possible_types = []

    for cur_type in types.keys():
        count = types[cur_type]
        result = ""
        i = 0 
        while i < len(s):
            if s[i:i+len(cur_type)].lower() == cur_type: 
                
                result += s[i:i+len(cur_type)] + "_" + str(count) 
                count += 1 
                i += len(cur_type) 

                types[cur_type] += 1
                possible_types.append(cur_type)
            else:
                result += s[i] 
                i += 1
        
        s = result
    return s, possible_types

import itertools

def all_subsets(input_set):
    subsets = []
    for i in range(len(input_set) + 1):
        subsets.extend(itertools.combinations(input_set, i))
    return subsets

if __name__ == "__main__":
  outputs = "./outputs"
  if not os.path.exists(outputs):
    os.makedirs(outputs)

  library = "torch"
  outputs_library = os.path.join(outputs, library)
  if not os.path.exists(outputs_library):
    os.makedirs(outputs_library)

  prompt_path = os.path.join(outputs_library, "Prompts.jsonl")
  output_path = os.path.join(outputs_library, "output.jsonl")
  INDEX_path = os.path.join(outputs_library, "INDEX.pkl")

  if os.path.exists(os.path.join(outputs_library, "output.jsonl")):
      continue_analysis(outputs_library)
      exit(0)


  '''
    Get generated mutators for various data types
  '''
  unique_mutators_path = "unique_mutators.json"
  if os.path.exists(unique_mutators_path):
    with open(unique_mutators_path, 'r') as json_file:
      unique_mutators = json.load(json_file)
  else:
      print("There is no", unique_mutators_path)
      exit(0)

  individual_mutators = {}
  pattern_mutators = {}
  for pattern, mutators in unique_mutators.items():
    pattern_list = eval(pattern)

    if len(pattern_list) == 1:
      individual_mutators[pattern_list[0][:-2]] = mutators
    else:
      pattern_mutators[pattern] = {}

      var_with_type = []
      tmp = []
      for var in pattern_list:
        tmp.append(var[:-2])
        var_with_type.append((var, var[:-2]))
      

      pattern_mutators[pattern]["list"] = sorted(tmp)
      pattern_mutators[pattern]["mutators"] = mutators
      pattern_mutators[pattern]["var_with_type"] = var_with_type

  #   print(pattern)
  #   for mutator in mutators:
  #     print(mutator)
  #   print("\n")

  # exit(0)
  
  # print("===== individual_mutators =====")
  # for pattern, mutators in individual_mutators.items():
  #   print(pattern)
  #   for mutator in mutators:
  #     print(mutator)
  #   print("\n")

  # exit(0)

  # print("===== pattern_mutators =====")
  # for pattern, info in pattern_mutators.items():
  #   print(pattern)
  #   print("list:", info["list"])
  #   for mutator in info["mutators"]:
  #     print(mutator)
  #   print("\n")

  '''
    Get the description for all target APIs
  '''
  api_description_path = "../get_api_reference_from_help/results/torch/api_description.json"
  if os.path.exists(api_description_path):
      print("api_description has been extracted")
      with open(api_description_path, 'r') as json_file:
          captured_infos = json.load(json_file)
  else:
      print("There is no api_description.json.")
      exit(0)

  # for api_name, info in captured_infos.items():
  #     print("\n\n==========", api_name, "==========")
  #     info = info.split('\n')
  #     info = '\n'.join(info[:10])

  #     print(info)
      
  # exit(0)

  '''
    Get initial programs for all APIs
  '''
  initial_programs_path = "api_programs.json"
  if os.path.exists(initial_programs_path):
    with open(initial_programs_path, 'r') as json_file:
      api_programs = json.load(json_file)
  else:
    print("There is no", initial_programs_path)
    exit(0)

  '''
    Get all parameters that the target APIs have
  '''
  api_info_path = "../get_api_reference_from_help/results/torch/apis_info.json"
  if os.path.exists(api_info_path):
      print("api_info_path has been extracted")
      with open(api_info_path, 'r') as json_file:
          api_info = json.load(json_file)
  else:
      print("There is no apis_info.json.")
      exit(0)

  all_type_pattern = []

  processed_api_info = {}
  for api_name, var_and_type in api_info.items():
    

    # print(api_name)
    type_collection = []

    if len(var_and_type) > 10: # If a apis has too many parameters, there may be some problems in it -> Thus, we skip these apis
      continue
    
    processed_api_info[api_name] = {}

    for var_name, var_tpye in var_and_type.items():
      if len(var_tpye) > 20: # If var_tpye is too long, there may be some problems in it -> Thus, we skip these types
        continue
      
      if var_tpye.lower() == "unknown" or var_tpye.lower() == "none":
        continue

      flag = 0
      for t in ["tensor", "int", "bool", "str", "float", "scalar", "list"]:
        if t in var_tpye.lower():
          flag = 1
          break
      
      if flag == 0:
        continue

      

      # print(var_name, ":", var_tpye)

      if var_tpye not in all_type_pattern:
        all_type_pattern.append(var_tpye)

      # cnt = 1
      # tmp = var_tpye.lower() + "_" + str(cnt)
      
      # while tmp in type_collection:
      #     cnt += 1
      #     tmp = var_tpye.lower() + "_" + str(cnt)

      processed_api_info[api_name][var_name] = var_tpye
    # print("\n")
  
  # show processed_api_info
  print("==== show processed_api_info ====")
  need_to_be_mutated = 0
  skip = 0
  individual_cnt = 0
  pattern_cnt = 0

  
  allData = []
  INDEX = {}
  cnt = 0
  system = "You are an advanced Language Model assistant that can generate, execute, and evaluate code. Please use Markdown syntax to represent code blocks."
  for api_name, var_and_type in processed_api_info.items():
    cur_individual_cnt = 0
    cur_pattern_cnt = 0

    analysis = 0
    if var_and_type == {}:
      skip += 1
    else:
      analysis = 1
      need_to_be_mutated += 1
    
    if analysis == 0:
      continue

    if api_programs[api_name] == "none":
      continue
    
    print("api_name:", api_name)

    # Get the description of the current API
    info = captured_infos[api_name].split('\n')
    info = '\n'.join(info[:10])
    # print("\n---- info start ----")
    # print(info)
    # print("---- info end ----\n")

    # print("\n---- init program start ----")
    # print(api_programs[api_name])
    # print("---- init program end ----\n")


    '''
      The strategy for individual mutation: 
        - For the parameters that could be multiple types, we try 1/8 mutators.
        - For the first two parameters, we try all mutators.
        - For the 2-4 parameters, we try 1/4 mutators.
        - For the 4+ parameters, we try 1/8 mutators.
    '''
    
    
    types = {"tensor": 1, "int": 1, "bool": 1, "str": 1, "float": 1, "scalar": 1, "list": 1}
    pattern_candidates = {}
    type_to_var = {}
    var_with_type = []
    var_cnt = 0
    for var_name, var_tpye in var_and_type.items():
      var_cnt += 1

      var_tpye_new, possible_types = add_suffix_to_type(var_tpye, types)

      if var_tpye.lower() in ["tensor", "int", "bool", "str", "float", "scalar", "list"]:
        # pattern_candidates[var_tpye_new] = var_tpye.lower()
        pattern_candidates[var_name] = var_tpye.lower()
        type_to_var[var_tpye_new] = var_name

        var_with_type.append((var_name, var_tpye.lower()))
      
      # mutate the parameter individually
      # For the parameters that could be several data types, 
      # we just consider it as a individual parameter that can not be combined with other parameters to construct a complex data type pattern.
      # print(var_name, ":", var_tpye_new)

      # Find out we can use which mutators
      ## Check each var can be which types
      # print("possible_types:", possible_types)

      ## For each possible type, we construct corresponding mutators for it
      tmp_prompts = []
      for cur_type in possible_types:
        # get mutator
        # print("\ncur_type:", cur_type)
        if cur_type not in individual_mutators.keys():
          continue

        mutators_for_cur_type = individual_mutators[cur_type]

        for cur_mutator in mutators_for_cur_type:
          # print(cur_mutator)

          # For each mutator, you need to create a prompt to mutate the program
          tmp = copy.deepcopy(mutator_template)
          tmp = tmp.replace("<N>", "1")
          tmp = tmp.replace("<VAR>", var_name)
          tmp = tmp.replace("<API>", api_name)
          tmp = tmp.replace("<REQUIREMENT>", cur_mutator)

          prompt = copy.deepcopy(mutation_prompt_template)
          prompt = prompt.replace("<INIT_PROGRAM>", api_programs[api_name])
          prompt = prompt.replace("<API_INFO>", info)
          prompt = prompt.replace("<API>", api_name)
          prompt = prompt.replace("<MUTATORS>", tmp)

          

          tmp_prompts.append(prompt)

          # print("\n---- prompt start ----")
          # print(prompt)
          # print("---- prompt end ----\n")
      
      
      if len(possible_types) > 1:
        rate = 0.125
      else:
        rate = 1

      if var_cnt <= 2:
        pass
      elif var_cnt <= 4:
        rate *= 0.25
      else:
        rate *= 0.125
      
      # the minimum of rate is 0.1
      if rate < 0.1:
        rate = 0.1
      
      if rate != 1:
        target_num = int(rate * len(tmp_prompts))
        if target_num < 1:
          target_num = 1
        final_prompts = random.sample(tmp_prompts, target_num)

        print(var_tpye, "=> ori num:", len(tmp_prompts), "->", "cur num:", target_num)
      else:
        final_prompts = tmp_prompts
        print(var_tpye, "->", len(tmp_prompts),)
      
      # save final_prompts
      for tmp_prompt in final_prompts:
        individual_cnt += 1
        cur_individual_cnt += 1

        INDEX[api_name + "-" + str(cnt)] = cnt
        allData.append({"index":cnt, "instruction":system, "input":tmp_prompt})
        cnt += 1
      


      

    print("cur_individual_cnt:", cur_individual_cnt)

    # print("\n===== Pattern Mutation =====")    
    # For the parameters that must be a specific data type, we consider combining it with other parameters to construct a complex data type pattern.
    # print(pattern_candidates)
    # print(type_to_var)
    # print("var_with_type:", var_with_type)

    var_list = []
    for var_name, var_type in pattern_candidates.items():
      var_list.append(var_name)
    
    all_patterns = all_subsets(var_list)
    # print(all_patterns)

    for cur_pattern in all_patterns:
      if len(cur_pattern) <= 1:
        continue

      print("\ncur_pattern:", cur_pattern)
      type_list = []
      pattern_var_to_type = []
      for var in cur_pattern:
        type_list.append(pattern_candidates[var])
        pattern_var_to_type.append((var, pattern_candidates[var]))
      
      type_list = sorted(type_list)

      # target_vars = []
      # for _, var_name in type_to_var.items():
      #   target_vars.append(var_name)
      # print("target_vars:", target_vars)

      


      # print("type_list:", type_list)

      # check if the type_list matches a mutator
      target_pattern_mutators = None
      pattern_var_with_type = None
      for pattern, info_tmp in pattern_mutators.items():
        if info_tmp["list"] == type_list:
          target_pattern_mutators = info_tmp["mutators"]
          pattern_var_with_type = info_tmp["var_with_type"]
          
          break
      
      if not target_pattern_mutators:
        continue

      var_with_type_sorted = sorted(pattern_var_to_type, key=lambda x: x[1])
      pattern_var_with_type_sorted = sorted(pattern_var_with_type, key=lambda x: x[1])

      related_vars = [tpl[0] for tpl in var_with_type_sorted]

      print("related_vars:", related_vars)

      print("\n---- vars mapping start ----")
      for i in range(len(var_with_type_sorted)):
        print(var_with_type_sorted[i][0], "->", pattern_var_with_type_sorted[i][0])
      print("---- vars mapping end ----\n")

      print("var_with_type_sorted:", var_with_type_sorted)
      print("pattern_var_with_type_sorted:", pattern_var_with_type_sorted)

      for cur_pattern_mutator in target_pattern_mutators:
        # print(cur_pattern_mutator)
        
        for i in range(len(var_with_type_sorted)):
          cur_pattern_mutator = cur_pattern_mutator.replace(pattern_var_with_type_sorted[i][0], var_with_type_sorted[i][0])
        
        print("cur_pattern_mutator:", cur_pattern_mutator)


        # For each mutator, you need to create a prompt to mutate the program
        tmp = copy.deepcopy(mutator_template)
        tmp = tmp.replace("<VAR>", str(related_vars))
        tmp = tmp.replace("<API>", api_name)
        tmp = tmp.replace("<REQUIREMENT>", cur_pattern_mutator)

        prompt = copy.deepcopy(mutation_prompt_template)
        prompt = prompt.replace("<INIT_PROGRAM>", api_programs[api_name])
        prompt = prompt.replace("<API_INFO>", info)
        prompt = prompt.replace("<API>", api_name)
        prompt = prompt.replace("<MUTATORS>", tmp)

        # print("\n---- prompt start ----")
        # print(prompt)
        # print("---- prompt end ----\n")

        INDEX[api_name + "-" + str(cnt)] = cnt
        allData.append({"index":cnt, "instruction":system, "input":prompt})
        cnt += 1

        pattern_cnt += 1
        cur_pattern_cnt += 1
        # exit(0)

    # exit(0)

    # find out we can use which mutators

    
    print("cur_pattern_cnt:", cur_pattern_cnt)
    print("\n")

  
  

  

  # for pattern in all_type_pattern:
  #   print(pattern)

  # print("need_to_be_mutated:", need_to_be_mutated)
  # print("skip:", skip)

  print("pattern_cnt:", pattern_cnt)
  print("individual_cnt:", individual_cnt)

  with open(prompt_path, 'w') as file:
    for item in allData:
        json.dump(item, file)
        file.write('\n')

  with open(INDEX_path, "wb") as file:
    pickle.dump(INDEX, file)