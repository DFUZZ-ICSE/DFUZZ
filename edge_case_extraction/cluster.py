import re
import os
import clang.cindex
from tqdm import tqdm

def read_file(filename):
    code = []
    with open(filename, 'r') as file:
        for line in file:
            code.append(line)
    return code
            

def extract_functions_from_code(code):
    pattern = r'(\w+)\s+(\w+)\('
    res = []
    cnt = 0
    for line in code:
        if ";" not in line:
            functions = re.findall(pattern, line)
            if functions:
                # print(functions)
                res.append(cnt)
        
        cnt += 1

    return res

def extract_check_from_code(code, features):
    res = []
    res_details = {}
    cnt = 0
    for line in code:
        if any(feature in line for feature in features):
            res.append(cnt)

            end = cnt
            while ";\n" not in code[end]:
                end += 1

            # cnt: the start line of the check statement 
            # end: the end line of the check statement
            pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
            origin_check_statement = " ".join(code[cnt:end+1])
            check_statement = origin_check_statement.split(",")[0] # only focus on the first parameter of the TORCH_CHECK because the latter parameters are not necessary
            tmp = re.findall(pattern, check_statement)
            res_details[cnt] = ([cnt, end], tmp, origin_check_statement)

        cnt += 1

    return res, res_details

def common_elements(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    common = set1.intersection(set2)
    return common

def extract_function_header(code, start_line):
    tmp = ""
    l = start_line
    while "{" not in code[l]:
        tmp += code[l]
        l += 1
    tmp += code[l]

    return tmp

def replace_variables(code_line, variable_map):
    pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
    variables = re.findall(pattern, code_line)
    
    for var in variables:
        if var in variable_map:
            # code_line = re.sub(r'\b{}\b'.format(re.escape(var)), variable_map[var], code_line)
            code_line = re.sub(r'\b{}\b'.format(re.escape(var)), '<{}>'.format(variable_map[var]), code_line)
    
    return code_line.replace("\n", " ")

def insert_string(original_string, substring, insert_string):
    index = original_string.find(substring)
    if index != -1:
        return original_string[:index] + insert_string + original_string[index:]
    else:
        return original_string

repeated_item = 0

def classify_elements(code, elements, boundaries, function_para, check_lines_details, sketelon_database, check_id):
    global repeated_item

    code_block_pool = []

    sorted_boundaries = sorted(boundaries, reverse=True)
    
    categories = {boundary: [] for boundary in sorted_boundaries}
    categories['<'+str(sorted_boundaries[-1])] = []

    for element in elements:
        placed = False
        for boundary in sorted_boundaries:
            if element >= boundary:
                categories[boundary].append(element)
                placed = True
                break
        if not placed:
            categories['<'+str(sorted_boundaries[-1])].append(element)

    check_to_id = {}
    discraded_elements = []
    expected_elements = []
    all_useful_elements = [] # record all useful check statement in a file
    for boundary, elems in categories.items():
        
        print(f" {boundary}: {elems}")
        if elems:
            useful_element = []
            cur_function_para = function_para[boundary]
            print("cur_function_para:", cur_function_para)
            for element in elems:
                cur_check_details = check_lines_details[element][1]
                cur_check_start = check_lines_details[element][0][0]
                cur_check_end = check_lines_details[element][0][1]
                cur_raw_statement = check_lines_details[element][2]

                print("element:", element)
                print("cur_check_details:", cur_check_details)

                cur_function_header = extract_function_header(code, boundary).replace("\n", " ")
                function_header_para_to_type = {}
                for tmp_para in cur_function_para:
                    tmp_idx = cur_function_header.find(tmp_para)
                    substr = cur_function_header[:tmp_idx]
                    start_index = max(substr.rfind('('), substr.rfind(','))
                    substr = substr[start_index+1:]
                    function_header_para_to_type[tmp_para] = substr.strip()
                print("cur_function_header:", cur_function_header)
                print("function_header_para_to_type:", function_header_para_to_type)

                # res_details[cnt] = ([cnt, end], tmp)
                skip = False
                if common_elements(cur_function_para, cur_check_details):
                    difference = [item for item in cur_check_details if item not in cur_function_para]
                    # difference.remove('TORCH_CHECK')
                    # print("difference:", difference)
                    
                    for diff_item in difference:
                        if diff_item == 'TORCH_CHECK':
                            continue
                        diff_idx = cur_raw_statement.find(diff_item)
                        if cur_raw_statement[diff_idx - 1] != '.':
                            skip = True

                    if not skip:
                        

                        dot_idx = cur_raw_statement.find(',')
                        check_core = cur_raw_statement[:dot_idx]
                        check_core = check_core.replace(' ', '')
                        check_core = check_core.replace('\n', '')
                        sketelon = replace_variables(check_core, function_header_para_to_type)

                        # for tmp_para in cur_function_para:
                        #     sketelon = sketelon.replace(tmp_para, function_header_para_to_type[tmp_para])
                        print("cur_raw_statement:", check_core)
                        print("sketelon:", sketelon.strip())
                            
                        if sketelon.strip() not in sketelon_database:
                            sketelon_database.append(sketelon.strip())

                            check_to_id[element] = check_id[0]
                            check_id[0] += 1

                            useful_element.append(element)
                            all_useful_elements.append(element)
                            for i in range(cur_check_start, cur_check_end+1):
                                expected_elements.append(i)
                        else:
                            skip = True
                            repeated_item += 1
                
                if skip:
                    for i in range(cur_check_start, cur_check_end+1):
                        discraded_elements.append(i)
                print("discraded_elements:", discraded_elements)
            
            if not useful_element:
                continue
                    
            code_block = [boundary, max(useful_element)]
            print(code_block)
            code_block_pool.append(code_block)

    for code_block in code_block_pool:
        while ";\n" not in code[code_block[1]]:
            code_block[1] += 1


    check_codes = []

    for code_block in code_block_pool:
        tmp = ""

        print(code_block)
        # print(code[code_block[0]])
        # print(code[code_block[1]])
        print("----------- Target code block start -------------")
        # print(code[code_block[0]:code_block[1]+1])
        l = code_block[0]

        # To improve the performance of LLM, we just extract the function header and the related check statements
        ## extract the function header
        while "{" not in code[l]:
            tmp += code[l]
            print(code[l])
            l += 1

        print(code[l])
        tmp += code[l]

        ## extract the check statements
        while l <= code_block[1]:
            if l in discraded_elements:
                l += 1
                continue

            if l not in expected_elements:
                l += 1
                continue

            if l in all_useful_elements:
                tmp += code[l]
                # use to add check_id
                # tmp += insert_string(code[l], "TORCH_CHECK", "\n//(" + str(check_to_id[l]) + ")\n ")

                # check_id[0] += 1
            else:
                tmp += code[l]
            print(code[l])
            l += 1
        print("----------- Target code block end -------------")

        check_codes.append(tmp)

    return check_codes



def extract_functions_from_cpp(filename):
    index = clang.cindex.Index.create()
    tu = index.parse(filename)
    functions_info = []

    for node in tu.cursor.walk_preorder():
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            functions_info.append((node.spelling, node.extent.start.line))
        elif node.kind == clang.cindex.CursorKind.CXX_METHOD:
            functions_info.append((node.spelling, node.extent.start.line))
        elif node.kind == clang.cindex.CursorKind.FUNCTION_TEMPLATE:
            if node.kind == clang.cindex.CursorKind.FUNCTION_TEMPLATE:
                functions_info.append((node.spelling, node.extent.start.line))

    return functions_info

def extract_functions_from_cpp2(filename):
    index = clang.cindex.Index.create()
    tu = index.parse(filename)
    functions_info = []

    for node in tu.cursor.walk_preorder():
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL or node.kind == clang.cindex.CursorKind.CXX_METHOD:
            parameters = []
            for arg in node.get_arguments():
                parameters.append(arg.displayname)
            functions_info.append((node.spelling, node.extent.start.line, parameters))

    return functions_info

def check_empty_list(lst):
    for element in lst:
        if element != '':
            return False
    return True

def analyze_cpp_file_main(path, features, sketelon_database, check_id):

    functions_info = extract_functions_from_cpp2(path)
    function_lines = []
    function_para = {}
    for func_name, start_line, parameters in functions_info:
        if check_empty_list(parameters):
            continue
        # print(f"Function: {func_name}, Start Line: {start_line}")
        function_lines.append(start_line - 1)
        function_para[start_line - 1] = parameters


    code = read_file(path)
    # function_lines = extract_functions_from_code(code)

    check_lines, check_lines_details = extract_check_from_code(code, features)

    print("function_para:", function_para)
    print("check_lines_details:", check_lines_details)

    function_lines.sort(reverse=True)
    check_lines.sort(reverse=True)

    print("function_lines:", function_lines)
    print("check_lines:", check_lines)

    if len(check_lines) == 0 or len(function_lines) == 0:
        print("=== No check lines or function lines found ===")
        print("path:", path)
        return None

    function_lines = [num for num in function_lines if num < check_lines[0]]
    if len(function_lines) == 0:
        return None
    check_lines = [num for num in check_lines if num > function_lines[-1]]
    if len(check_lines) == 0:
        return None
    print("function_lines 1:", function_lines)
    print("check_lines 1:", check_lines)

    

    check_codes = classify_elements(code, check_lines, function_lines, function_para, check_lines_details, sketelon_database, check_id)


    # for code_block in code_block_pool:
    #     print(code_block)
    #     # print(code[code_block[0]])
    #     # print(code[code_block[1]])
    #     print("----------- Target code block start -------------")
    #     # print(code[code_block[0]:code_block[1]+1])
    #     for l in code[code_block[0]:code_block[1]+1]:
    #         print(l)
    #     print("----------- Target code block end -------------")
    #     res.append(code[code_block[0]:code_block[1]+1])
    return check_codes

def find_cpp_files(directory):
    cpp_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".cpp"):
                cpp_files.append(os.path.join(root, file))
    return cpp_files


import json
import time
import random
import openai
import copy

def embedding(str, max_retries = 20, model = "text-embedding-ada-002"):
    
    with open('./config.json', 'r') as file:
        data = json.load(file)
    api_keys = data['api_keys']
    api_base = data['api_base']


    # for key in api_keys:
    attempts = 0
    completion = None
    while attempts < max_retries:
        key = random.choice(api_keys)
        # print("key:", key)
        try:
            openai.api_key = key
            openai.api_base = api_base
            completion = openai.Embedding.create(
                model=model,
                input=str
            )
            break
        except Exception as e:
            attempts += 1
            print(e)

            if attempts == max_retries:
                time.sleep(60)
                attempts = 0


    if not completion:
        return None

    output = completion["data"][0]["embedding"]
    return output

def request_openai_api(messages, max_retries = 20, temperature = 0, model = "GPT-3.5"):

    if model == "GPT-3.5":
        model = "gpt-3.5-turbo-1106"

        with open('./config.json', 'r') as file:
            data = json.load(file)
        api_keys = data['api_keys']

    elif model == "GPT-4":
        model = "gpt-4-0125-preview"
        # model = "gpt-4-1106-preview"

        with open('./config-gpt-4.json', 'r') as file:
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



def messages_gen(prompt, messages_template):

    messages = copy.deepcopy(messages_template)
    messages[-1]["content"] = prompt

    # prompt = feature_prompt_reask.replace("<TARGET>", TARGET)
    # messages.append({"role": "user", "content": prompt})
    
    return messages


def extract_vars_and_types(input_str):
    # pattern = r'(\w+)\((\w+)\)'
    pattern = r'(\w+)\(([^)]+)\)'
    matches = re.findall(pattern, input_str)
    vars_and_types = [(match[0], match[1]) for match in matches]
    return vars_and_types

def contains_pattern(input_str):
    pattern = r'<(tensor|int|bool|str|float|scalar|list)>\s+`(\w+)`'
    match = re.search(pattern, input_str)
    return bool(match)

def extract_types(input_str):
    types = re.findall(r'\b(\w+)\s+`', input_str)
    return types

def remove_backticks(input_str):
    pattern = r'`(.*?)`'
    result = re.sub(pattern, '', input_str)
    return result

def extract_res_last_time(raw_llm):
    valid = 0
    res = None

    print("\n***** RES ANLAYSIS START *****")
    print("Raw LLM:")
    print(raw_llm)
    print("\n")

    msgs = []
    mutators = []

    # read the reponse
    try:
        data = json.loads(raw_llm)
    except Exception as e:
        msg = "Error parsing JSON: " + str(e) + " -> Directly output the JSON content without any additional output (e.g., no need for code delimiters like ```)."
        msgs.append(msg)

        return valid, msg

    

    for check in data.keys():

        check_info = {}
        for key, value in data[check].items():
            if "variable" in key.lower():
                check_info["variable"] = value
            elif "TORCH_CHECK" in key:
                check_info["TORCH_CHECK"] = value
            elif "requirement" in key.lower():
                check_info["Requirement"] = value

        print("-- check_info:", check_info)

        # check if "variable" and "Requirement" exist in the response
        if "variable" not in check_info.keys():
            msg = '''No related input variables is extracted. -> List the name and type of the related input variables (defined in the function header), and use comma to separate, such as "var1(type1), var2(type2)". If this TORCH_CHECK statement is not directly related to input variables, return 'None'.'''
            msgs.append(msg)
            continue
        
        if "Requirement" not in check_info.keys():
            msg = '''No requirement is extracted. -> whether the variables satisfy what requirements. Answer this question following "<the type> `<variable name>` should <requirement>", such as "the tensor input_t shuold be a 2D tensor". Note that variable names should be enclosed in backticks(``).'''
            msgs.append(msg)
            continue

        if check_info["variable"] == "None" and check_info["Requirement"] == "None":
            continue


        # check 1: check if the related input variables extracted from raw_llm is valid. Note that we skip the special case that the related input variables are none.
        ## output format: check if we can extract the corresponding results
        print("---- check variable")
        
        variables = check_info["variable"]
        vars_and_types = extract_vars_and_types(variables)
        if not vars_and_types:
            msg = '''You have not list the variables' names and types "The checked input variables" as required -> List the name and type of the related input variables (defined in the function header), and use comma to separate, such as "var1(type1), var2(type2)". If this TORCH_CHECK statement is not directly related to input variables, return 'None'.'''
            msgs.append(msg)
            continue

        print("------ vars_and_types:", vars_and_types)
        ## the types of input variables: check if these types in our 
        var_to_type = {}
        type_collection = []
        for var, type in vars_and_types:
            if type.lower() not in ["tensor", "int", "bool", "str", "float", "scalar", "list"]:
                msg = type + " is not considered -> Considering only the following variable types: {Tensor, Int, Bool, Str, Float, Scalar, List}. Otherwise, return 'None'."
                msgs.append(msg)
                continue

            tmp = type.lower()
            cnt = 1
            while tmp in type_collection:
                tmp = type.lower() + "_" + str(cnt)
                cnt += 1
            var_to_type[var] = tmp
            type_collection.append(tmp)

        print("------ var_to_type:", var_to_type)

        print("---- check Requirement")
        # check 2: check if the extracted requirements contain input variables in valid format
        check_requirement = check_info["Requirement"].lower()
        vars = re.findall(r'`([^`]+)`', check_requirement)
        if not vars:
            msg = '''The format of variables in the Requirement is not in the valid format -> Answer this question following "`<variable name>` should <requirement>", such as "the `input_t` shuold be a 2D tensor". Note that variable names should be enclosed in backticks(``).'''
            continue
        vars = list(set(vars))
        types = []
        for var in vars:
            if var not in var_to_type.keys():
                msg = "The variables used in 'Requirement' is not compatible with the 'The checked input variables' -> Please check the 'Requirement' and the 'The checked input variables'."
                continue
            types.append(var_to_type[var])
            check_requirement = check_requirement.replace("`" + var + "`", "`" + var_to_type[var] + "`")
        
        mutators.append({"types": types, "mutator": check_requirement})
            

        # types = extract_types(check_info["Requirement"].lower())
        # print("------ types:", types)
        # save_flag = True
        # for type in types:
        #     if type.lower() not in ["tensor", "int", "bool", "str", "float", "scalar", "list"]:
        #         save_flag = False

        # if save_flag and types:
        #     mutator = remove_backticks(check_info["Requirement"])
        #     mutators.append({"types": types, "mutator": mutator})
        # else:
        #     msg = '''The format of requirement `{requirement}` is not valid. -> Answer this question following "<the type> `<variable name>` should <requirement>", such as "the tensor input_t shuold be a 2D tensor". Note that variable names should be enclosed in backticks(``).'''
        #     msgs.append(msg)
        #     return 0, msg

    print("msgs:", msgs)
    print("mutators:", mutators)

    print("***** RES ANLAYSIS END *****\n")

    return 1, mutators

def extract_res(raw_llm):
    valid = 0
    res = None

    print("\n***** RES ANLAYSIS START *****")
    print("Raw LLM:")
    print(raw_llm)
    print("\n")

    msgs = []
    mutators = []

    # read the reponse
    try:
        data = json.loads(raw_llm)
    except Exception as e:
        msg = "Error parsing JSON: " + str(e) + " -> Directly output the JSON content without any additional output (e.g., no need for code delimiters like ```)."
        msgs.append(msg)

        return valid, msg

    

    for check in data.keys():

        check_info = {}
        for key, value in data[check].items():
            if "variable" in key.lower():
                check_info["variable"] = value
            elif "TORCH_CHECK" in key:
                check_info["TORCH_CHECK"] = value
            elif "requirement" in key.lower():
                check_info["Requirement"] = value

        print("-- check_info:", check_info)

        # check if "variable" and "Requirement" exist in the response
        if "variable" not in check_info.keys():
            msg = '''No related input variables is extracted. -> List the name and type of the related input variables (defined in the function header), and use comma to separate, such as "var1(type1), var2(type2)". If this TORCH_CHECK statement is not directly related to input variables, return 'None'.'''
            msgs.append(msg)
            return 0, msg
        
        if "Requirement" not in check_info.keys():
            msg = '''No requirement is extracted. -> whether the variables satisfy what requirements. Answer this question following "<the type> `<variable name>` should <requirement>", such as "the tensor input_t shuold be a 2D tensor". Note that variable names should be enclosed in backticks(``).'''
            msgs.append(msg)
            return 0, msg

        if check_info["variable"] == "None" and check_info["Requirement"] == "None":
            continue


        # check 1: check if the related input variables extracted from raw_llm is valid. Note that we skip the special case that the related input variables are none.
        ## output format: check if we can extract the corresponding results
        print("---- check variable")
        
        variables = check_info["variable"]
        vars_and_types = extract_vars_and_types(variables)
        if not vars_and_types:
            msg = '''You have not list the variables' names and types "The checked input variables" as required -> List the name and type of the related input variables (defined in the function header), and use comma to separate, such as "var1(type1), var2(type2)". If this TORCH_CHECK statement is not directly related to input variables, return 'None'.'''
            msgs.append(msg)
            return 0, msg

        print("------ vars_and_types:", vars_and_types)
        ## the types of input variables: check if these types in our 
        var_to_type = {}
        type_collection = []
        for var, type in vars_and_types:
            if type.lower() not in ["tensor", "int", "bool", "str", "float", "scalar", "list"]:
                msg = type + " is not considered -> Considering only the following variable types: {Tensor, Int, Bool, Str, Float, Scalar, List}. Otherwise, return 'None'."
                msgs.append(msg)
                return 0, msg

            tmp = type.lower()
            cnt = 1
            while tmp in type_collection:
                tmp = type.lower() + "_" + str(cnt)
                cnt += 1
            var_to_type[var.lower()] = tmp
            type_collection.append(tmp)

        print("------ var_to_type:", var_to_type)

        print("---- check Requirement")
        # check 2: check if the extracted requirements contain input variables in valid format
        check_requirement = check_info["Requirement"].lower()
        vars = re.findall(r'`([^`]+)`', check_requirement)
        if not vars:
            msg = '''The format of variables in the Requirement is not in the valid format -> Answer this question following "`<variable name>` should <requirement>", such as "the `input_t` shuold be a 2D tensor". Note that variable names should be enclosed in backticks(``).'''
            return 0, msg
        vars = list(set(vars))
        types = []
        for var in vars:
            if var not in var_to_type.keys():
                msg = "The variables used in 'Requirement' is not compatible with the 'The checked input variables' -> Please check the 'Requirement' and the 'The checked input variables'."
                return 0, msg
            types.append(var_to_type[var])
            check_requirement = check_requirement.replace("`" + var + "`", "`" + var_to_type[var] + "`")
        
        mutators.append({"types": types, "mutator": check_requirement})
            

        # types = extract_types(check_info["Requirement"].lower())
        # print("------ types:", types)
        # save_flag = True
        # for type in types:
        #     if type.lower() not in ["tensor", "int", "bool", "str", "float", "scalar", "list"]:
        #         save_flag = False

        # if save_flag and types:
        #     mutator = remove_backticks(check_info["Requirement"])
        #     mutators.append({"types": types, "mutator": mutator})
        # else:
        #     msg = '''The format of requirement `{requirement}` is not valid. -> Answer this question following "<the type> `<variable name>` should <requirement>", such as "the tensor input_t shuold be a 2D tensor". Note that variable names should be enclosed in backticks(``).'''
        #     msgs.append(msg)
        #     return 0, msg

    print("msgs:", msgs)
    print("mutators:", mutators)

    print("***** RES ANLAYSIS END *****\n")

    return 1, mutators
        




def reask(dialog, extract_res, MAX_TRY):
    SUCCESS = 0
    try_cnt = 0
    while try_cnt < MAX_TRY:
        # print("\ntry_cnt:", try_cnt)
        print(dialog)
        raw_llm = request_openai_api(dialog, 20)
        print("raw_llm:", raw_llm)
        res, valid = extract_res(raw_llm) 
        print("res:", res)
        print("valid:", valid)

        if valid:
            SUCCESS = 1
            break
        else:
            dialog.append(
                {"role": "assistant", "content": raw_llm}
            )
            dialog.append(
                {"role": "user", "content": res + " Please generate again."}
            )

        try_cnt += 1

    
    if SUCCESS:
        return res, 1
    else:
        print("---- Can not finish this task. Here are the unsloved problem:", res)
        return None, 0


def iterative_analysis(init_mutaotr):
    finished = []
    waiting = []

    waiting.append(init_mutaotr)

    while waiting:
        # construct message
        construct_message()

    raw_llm = request_openai_api(dialog, 20)
    valid, res = extract_res(raw_llm) 

from collections import deque

# Q_template = """```
# the `int` should be greater than or equal to 6
# ```
# What sub-requirements can the above requirement be decomposed into? Output the results following "<num>. <sub-requirement>"""

# A_template = """1. The `int` should be greater than 6.
# 2. The `int` should be equal to 6."""

# prompt_template = """```
# <TARGET_MUTATOR>
# ```
# What sub-requirements can the above requirement be decomposed into? Output the results following "<num>. <sub-requirement>"""




Q_template = """```
the `int` should be greater than or equal to 6
```
Based on the relationships indicated by 'and/or', divide the aforementioned condition into distinct parts. If the above condition does not have "and/or" relationships, simply summarize the condition. Output the results following "<num>. <sub-requirement>"""

A_template = """1. The `int` should be greater than 6.
2. The `int` should be equal to 6."""

prompt_template = """```
<TARGET_MUTATOR>
```
Based on the relationships indicated by 'and/or', divide the aforementioned condition into distinct parts. If the above condition does not have "and/or" relationships, simply summarize the condition. Output the results following "<num>. <sub-requirement>"""




messages_template = [
    {"role": "system", "content": "You are a LLM."},
    {"role": "user", "content": Q_template},
    {"role": "assistant", "content": A_template},
    {"role": "user", "content": ""}
]

def construct_message(mutator):
    prompt = prompt_template.replace("<TARGET_MUTATOR>", mutator)

    messages = copy.deepcopy(messages_template)
    messages[-1]["content"] = prompt

    
    return messages

def extract_mutator(text):
    pattern = r'\d+\.\s*(.*)'
    matches = re.findall(pattern, text, flags=re.MULTILINE)

    res = []
    for info in matches:
        res.append(info.strip())

    if res:
        return res, 1
    else:
        msg = '''Output the results following "<num>. <sub-requirement>", such as "1. The `int` should be greater than 6.".'''
        return msg, 0

def decompose_element(init_mutaotr, decompose_res):
    print("\n======== decompose start ========")

    decomposition_result = []
    queue = deque([init_mutaotr])
    
    while queue:
        print("\nqueue:", queue)

        current_element = queue.popleft()
        print("current_element:", current_element)
        
        # construct message
        message = construct_message(current_element)
        
        res, valid = reask(message, extract_mutator, 5)
        print("res:", res)

        if not valid:
            decomposition_result.append(current_element)
            continue

        if len(res) == 1:
            decomposition_result.append(res)
            continue
        else:
            queue.extend(res)

    print("\norigin:", init_mutaotr)
    print("decomposition_result:", decomposition_result)
    decompose_res[init_mutaotr] = decomposition_result

    print("======== decompose end ========\n")
    
    return decomposition_result



# prompt_template = """The set of conditions = ```
# <UNIQUE_SET>
# ```

# Task 1: Among the above conditions, identify the items that have the same constraints as <MUTATOR>. if there are no such items, return 'None'.
# Task 2: Make a conclusion. Answer `Existent` or `Non-existent`. The conclusion should be enclosed in backticks(``), such as `Existent/Non-existent`."""

# prompt_template = """```
# <UNIQUE_SET>
# ```

# Task 1: Among the above conditions, find the items that have the same constraints as "MUTATOR". If there are no such items, proceed to the next task.
# Task 2: Answer `Yes` or `No`. The answer should be enclosed in backticks(``), such as `Yes/No`."""

Q_template_1 = """The set of conditions = ```1. the `tensor` tensor should be contiguous
2. the `tensor` should be nested
3. the `tensor` should have a dimension of 4 or 5
```

Among the above conditions, are there any items that have the same constraints as "the `tensor` should be 4d"? Answer `Yes` or `No`. The answer should be enclosed in backticks(``), such as `Yes/No`."""

A_template_1 = """Task 1: The item that has the same constraints as "the `tensor` should be 4d" is: "the tensor should have a dimension of 4 or 5".
Task 2: `Yes`"""

Q_template_2 = """The set of conditions = ```1. the `tensor` tensor should be contiguous
2. the `tensor` should be nested
3. the `tensor` should have a dimension of 4 or 5
```

Among the above conditions, are there any items that have the same constraints as "the `tensor` should be 7d"? Answer `Yes` or `No`. The answer should be enclosed in backticks(``), such as `Yes/No`."""

A_template_2 = """Task 1: there are no items that have the same constraints as "the `tensor` should be 7d".
Task 2: `No`"""

prompt_template = """
<UNIQUE_SET>
```

Among the above conditions, are there any items that have the same constraints as "MUTATOR"? Answer `Yes` or `No`. The answer should be enclosed in backticks(``), such as `Yes/No`."""

messages_template = [
    {"role": "system", "content": "You are a LLM."},
    {"role": "user", "content": Q_template_1},
    {"role": "assistant", "content": A_template_1},
    {"role": "user", "content": Q_template_2},
    {"role": "assistant", "content": A_template_2},
    {"role": "user", "content": ""}
]

verify_Q = """Is the constraint of "the `tensor` should be contiguous" the same as the constraint of "the `tensor` should be a non-empty 3d data tensor? Answer `Yes` or `No` and give the reason. The answer should be enclosed in backticks(``), such as `Yes/No`."""

verify_A = """`No`, these constraints are not the same.
1. "The tensor should be contiguous": This constraint refers to the memory layout of the tensor, as explained earlier. It means that the elements of the tensor are stored in a single, contiguous block of memory without any gaps or extra padding between them. This is typically a requirement for certain operations or optimizations in frameworks like PyTorch or TensorFlow.
2. "The tensor should be a non-empty 3D data tensor": This constraint specifies the shape and content of the tensor. It indicates that the tensor should have three dimensions (e.g., width, height, and depth in the case of image data), and it should contain actual data (i.e., not be empty). This constraint doesn't directly relate to the memory layout; rather, it concerns the structure and content of the tensor.
"""

verify_prompt_template = """Is the constraint of "MUTATOR_1" the same as the constraint of "MUTATOR_2"? Answer `Yes` or `No` and give the reason. The answer should be enclosed in backticks(``), such as `Yes/No`."""

verify_template = [
    {"role": "system", "content": "You are a LLM."},
    {"role": "user", "content": verify_Q},
    {"role": "assistant", "content": verify_A},
    {"role": "user", "content": ""}
]

prompt_template = """
```
<UNIQUE_SET>
```

Among the above conditions, are there any items that have the same constraints as "MUTATOR"? If exists, return the item that has the same constraints by enclosing in "{ }", such as {a condition}.
"""

messages_template = [
    {"role": "system", "content": "You are a coding expert."},
    {"role": "user", "content": ""}
]

def extract_res(raw_llm, mutator):
    pattern = r'\{([^{}]*)\}'
    matches = re.findall(pattern, raw_llm)
    if len(matches) == 0:
        return "non-existent", 1
    elif len(matches) == 1:
        if matches[0] == "" or matches[0].lower() == "none":
            return "non-existent", 1
    
    return matches[0], 1

    if "`yes`" in raw_llm.lower():
        return True, 1
    elif "`no`" in raw_llm.lower():
        return False, 1
    else:
        msg = "Among the above conditions, are there any items that have the same constraints as 'MUTATOR'. Answer 'Yes' or 'No'. The answer should be enclosed in backticks(``), such as `Yes/No`."
        msg = msg.replace("MUTATOR", mutator)
        return msg, 0
    

def reask(dialog, extract_res, MAX_TRY, mutator):
    SUCCESS = 0
    try_cnt = 0
    while try_cnt < MAX_TRY:
        print("-- try_cnt:", try_cnt)
        print(dialog)
        raw_llm = request_openai_api(dialog, 20)
        print("---- raw_llm start")
        print(raw_llm)
        print("---- raw_llm end")
        res, valid = extract_res(raw_llm, mutator) 
        # print("res:", res)
        # print("valid:", valid)

        if valid:
            SUCCESS = 1
            break
        else:
            dialog.append(
                {"role": "assistant", "content": raw_llm}
            )
            dialog.append(
                {"role": "user", "content": res + " Please generate again."}
            )

        try_cnt += 1

    
    if SUCCESS:
        return res, 1
    else:
        print("---- Can not finish this task. Here are the unsloved problem:", res)
        return None, 0

def analysis(unique_set, mutator):
    # construct prompt
    result = ""
    for i, item in enumerate(unique_set, start=1):
        result += f"{i}. {item}\n"
    prompt = prompt_template.replace("<UNIQUE_SET>", result)
    prompt = prompt.replace("MUTATOR", mutator)

    messages = copy.deepcopy(messages_template)
    messages[-1]["content"] = prompt

    # ask LLM
    res, valid = reask(messages, extract_res, 3, mutator)
    if valid:
        return res
    else:
        return None
    
def extract_res_verify(raw_llm, mutator):
    if "`yes`" in raw_llm.lower():
        return True, 1
    elif "`no`" in raw_llm.lower():
        return False, 1
    else:
        msg = "Answer `Yes` or `No` and give the reason. The answer should be enclosed in backticks(``), such as `Yes/No`."
        return msg, 0

def verify(mutator_1, mutator_2):
    print("----- verify start -----")
    # construct prompt
    prompt = verify_prompt_template.replace("MUTATOR_1", mutator_1)
    prompt = prompt.replace("MUTATOR_2", mutator_2)

    messages = copy.deepcopy(verify_template)
    messages[-1]["content"] = prompt

    # ask LLM
    res, valid = reask(messages, extract_res_verify, 3, "")

    print("----- verify end -----")
    if valid:
        return res
    else:
        return None


Q = """
```
the tensor should be a 1d tensor
the tensor should be a tensor on a cpu or cuda device
the tensor should have floating point or complex dtype
the tensor should be a 2d tensor
the tensor should have at least one dimension
the tensor should have more than 0 elements
the tensor should have at least 2 dimensions
```

Find a set of (tensor) that would violate all the above conditions simultaneously. The description of the (tensor): tensor refers to a data type of tensor.

Answer this question following these steps: 
Step I. Analyze each condition.
Step II. Create a set of (tensor) that violates all conditions simultaneously: "<num>. <The requirements of the (tensor)> (violates conditions X)".
Step II. Output the results in json format:
```json
{
	"index": {
		"data": "", # the description of the (tensor), such as "the (tensor) should be ..."
		"violate": "" # this (tensor) violates which conditions
	}
}
```
"""

A = """Step I. Analyze each condition:
1. 1d tensor: This condition is violated by tensors with more than one dimension.
2. Tensor on a CPU or CUDA device: We can create tensors on different devices to violate this condition.
3. Floating point or complex dtype: Tensors with other dtypes would violate this condition.
4. 2d tensor: This condition is violated by tensors with fewer or more than two dimensions.
5. At least one dimension: Tensors with zero dimensions (scalars) violate this condition.
6. More than 0 elements: Tensors with zero elements (empty tensors) violate this condition.
7. At least 2 dimensions: This condition is violated by tensors with fewer than two dimensions.

Step II. Create a set of tensors that violates all conditions simultaneously:
1. A scalar tensor with an integer dtype (violates conditions 1, 3, 4, 5, 6, and 7).
2. An empty tensor (zero elements) with any valid dtype (violates conditions 1, 2, 4, and 6).
3. A scalar tensor on a non-CPU/CUDA device (violates conditions 2, 3, 4, 5, 6, and 7).

Step III. Output:
```json
{
	"1": {
		"data": "A scalar tensor with an integer dtype",
		"violate": "violates conditions 1, 3, 4, 5, 6, and 7"
	}, 
	"2": {
		"data": "An empty tensor (zero elements) with any valid dtype",
		"violate": "violates conditions 1, 2, 4, and 6"
	}, 
	"3": {
		"data": "A scalar tensor on a non-CPU/CUDA device",
		"violate": "violates conditions 2, 3, 4, 5, 6, and 7"
	}, 
}
```"""

prompt_template = """
```
<MUTATORS>
```

Create a set of <DATA> that violate all conditions. Each condition will be violated by one/multiple <DATA>. <DESCRIPTION>

Output the results in JSON format:
```json
[
	{
		"data-description": "", # the description of the <DATA>
		"violated conditions": "" # the description of the conditions that this <DATA> violates, such as [CON_EXAMPLE]
	}
]
```

Directly output the JSON content without any additional output (e.g., no need for code delimiters like ```).
"""

messages_template = [
    {"role": "system", "content": "You are a LLM."},
    {"role": "user", "content": ""}
]

def var_replace(var):
    template = "SOURCE refers to a data type of TARGET. "
    if "tensor" in var:
        return template.replace("TARGET", "tensor").replace("SOURCE", var)
    elif "int" in var:
        return template.replace("TARGET", "int").replace("SOURCE", var)
    elif "bool" in var:
        return template.replace("TARGET", "bool").replace("SOURCE", var)
    elif "str" in var:
        return template.replace("TARGET", "str").replace("SOURCE", var)
    elif "float" in var:
        return template.replace("TARGET", "float").replace("SOURCE", var)
    elif "scalar" in var:
        return template.replace("TARGET", "scalar").replace("SOURCE", var)
    elif "list" in var:
        return template.replace("TARGET", "list").replace("SOURCE", var)

def read_mutators(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    all_mutators_unique = []
    for pattern in data:
        type_pattern = pattern["types"]
        mutator = pattern["mutator"]

        if not type_pattern:
            continue

        repeated = 0
        for unique_pattern in all_mutators_unique:
            type_pattern_unique = unique_pattern["types"]
            mutator_unique = unique_pattern["mutator"]
            if set(type_pattern_unique) == set(type_pattern) and mutator_unique == mutator:
                repeated = 1
                break
        
        if repeated == 0:
            all_mutators_unique.append(pattern)

    all_mutators_dict = {}
    pattern_description = {}

    for pattern in all_mutators_unique:
        type_pattern = sorted(pattern["types"])
        mutator = pattern["mutator"]

        res = "The description of the " + str(type_pattern).replace("'", "") + " is: "
        for var in type_pattern:
            res += var_replace(var)
        pattern_description[str(type_pattern)] = res

        if str(type_pattern) not in all_mutators_dict.keys():
            all_mutators_dict[str(type_pattern)] = []
        all_mutators_dict[str(type_pattern)].append(mutator)
    
    return all_mutators_dict, pattern_description

def extract_code(text):
    try:
        dataset = json.loads(text)
        violated_state = []
        for data in dataset:
            violated_state.append(data['violated conditions'])
        print("violated_state:", violated_state)
        target_idx = min_subset_cover_indices(violated_state)
        print("target_idx:", target_idx)

        mutators = []
        for idx in target_idx:
            mutators.append(dataset[idx]['data-description'])
        
        print("mutators:", mutators)
        return mutators, ""
            
    except Exception as e:
        msg = "Directly output the JSON content without any additional output (e.g., no need for code delimiters like ```)."
        return None, msg

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
        msg = "There is no json block in the response text."
        return None, msg

    if len(starts) != len(ends):
        msg = "The code blocks in the response text are not conforming to the Markdown syntax."
        return None, msg
    
    if len(starts) > 1:
        msg = "There are several code blocks in the response text. Please ensure that there is only one json block."
        return None, msg
    
    return "\n".join(lines[starts[0]+1:ends[0]]), ""

def min_subset_cover_indices(B):
    A = []
    for tmp in B:
        A.extend(tmp)
    A = set(A)

    B = [set(b) for b in B]  # Convert each list in B to a set
    cover_indices = []  # Initialize the list for indices of the cover
    original_B = list(B)  # Make a copy of B to remember original indices

    while A:  # While there are elements left to cover in A
        # Find the set in B that covers the most elements in A
        max_set = max(B, key=lambda s: len(s & A))
        cover_indices.append(original_B.index(max_set))  # Add the index of the found set
        A -= max_set  # Remove the covered elements from A
        B.remove(max_set)  # Remove the used set from B

        # Clean up B by removing sets that are now redundant
        B = [b for b in B if not b.issubset(max_set)]

    return cover_indices

def reask(dialog, extract_code, MAX_TRY):
    SUCCESS = 0
    try_cnt = 0
    while try_cnt < MAX_TRY:
        # print("\ntry_cnt:", try_cnt)
        print(dialog)
        # raw_llm = request_openai_api(dialog, 20, model = "GPT-4")
        raw_llm = request_openai_api(dialog, 20)
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
    


def analysis(groups, type_pattern, description):
    # construct prompt
    result = ""
    for i, item in enumerate(groups, start=1):
        result += f"{i}. {item}\n"
    prompt = prompt_template.replace("<MUTATORS>", result)
    prompt = prompt.replace("<DATA>", type_pattern)
    prompt = prompt.replace("<DESCRIPTION>", description)

    con_str = "\"" + groups[0] + "\", "
    if len(groups) > 1:
        con_str += "\"" + groups[1] + "\""
    prompt = prompt.replace("CON_EXAMPLE", con_str)

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
    


from sklearn.cluster import KMeans
def cluster(vectors, n_clusters, sentences):
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(vectors)
    labels = kmeans.labels_

    print(labels)

    clustered_sentences = {}

    for i, label in enumerate(labels):
        if label not in clustered_sentences:
            clustered_sentences[label] = [sentences[i]]
        else:
            clustered_sentences[label].append(sentences[i])

    return clustered_sentences

if __name__ == "__main__":
    filename = "all_mutators.json"
    res_name = "unique_mutators.json"

    if os.path.exists(res_name):
        with open(res_name, 'r') as json_file:
            unique_mutators = json.load(json_file)

            # for ori, res in decompose_res.items():
            #     print("ori:", ori)
            #     print("res:", res, "\n")
    else:
        unique_mutators = {}
    
    all_mutators_dict, pattern_description = read_mutators(filename)
    
    print("===== Cluster Start =====")
    all_clusters = {}
    cluster_name = "all_clusters.json"
    if os.path.exists(cluster_name):
        with open(cluster_name, 'r') as json_file:
            all_clusters = json.load(json_file)

    for type_pattern, mutators in all_mutators_dict.items():
        print("\n\ntype_pattern:", type_pattern)
        if type_pattern in all_clusters.keys():
            print(type_pattern, "has been analyzed.")
            continue

        print("num:", len(mutators))
        all_clusters[type_pattern] = []

        if len(mutators) > 5:
            n_clusters = int(len(mutators)/5) + 1
            print("n_clusters:", n_clusters)

            vectors = []
            for mutator in mutators:
                print(mutator)
                vector = embedding(mutator)
                vectors.append(vector)
            print("\n")

            print(len(vectors))
            for vec in vectors:
                print(len(vec))

            clustered_sentences = cluster(vectors, n_clusters, mutators)

            for cluster_idx, sentences_in_cluster in clustered_sentences.items():
                all_clusters[type_pattern].append(sentences_in_cluster)
                print("Cluster", cluster_idx, ":")
                for sentence in sentences_in_cluster:
                    print("-", sentence)
        else:
            all_clusters[type_pattern].append(mutators)
            print("do not need to be clustered")
        
        with open(cluster_name, 'w') as json_file:
            json.dump(all_clusters, json_file)

    print("all_clusters:", all_clusters)

    print("===== Cluster End =====")