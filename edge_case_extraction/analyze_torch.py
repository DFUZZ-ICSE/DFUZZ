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

def request_openai_api(messages, max_retries = 20, temperature = 0, model = "GPT-3.5"):
    with open('./config.json', 'r') as file:
        data = json.load(file)
    api_keys = data['api_keys']
    api_base = data['api_base']

    if model == "GPT-3.5":
        model = "gpt-3.5-turbo-1106"
    elif model == "GPT-4":
        model = "gpt-4-0125-preview"
    else:
        print("Invalid Model")

    start_time = time.time()

    # for key in api_keys:
    attempts = 0
    completion = None
    while attempts < max_retries:
        key = random.choice(api_keys)
        print("key:", key)
        try:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                api_key=key,
                request_timeout=20
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
    print("---- request time cost:", request_time)

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

    # pattern = r'\b(tensor|int|bool|str|float|scalar|list)\b\s*`(\w+)`'
    # matches = re.finditer(pattern, input_str)
    # types = []
    # result = []
    # for match in matches:
    #     var_type = match.group(1)
    #     var_name = match.group(2)
    #     result.append((var_type, var_name))
    #     types.append(var_type)
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

            cnt = 1
            tmp = type.lower() + "_" + str(cnt)
            
            while tmp in type_collection:
                cnt += 1
                tmp = type.lower() + "_" + str(cnt)

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

            cnt = 1
            tmp = type.lower() + "_" + str(cnt)
            
            while tmp in type_collection:
                cnt += 1
                tmp = type.lower() + "_" + str(cnt)
                
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
        




def reask(dialog, extract_res, MAX_TRY, all_mutators):
    SUCCESS = 0
    try_cnt = 0
    while try_cnt < MAX_TRY:
        print("* try_cnt:", try_cnt)
        # print(dialog)
        raw_llm = request_openai_api(dialog, 20)
        # print("raw_llm:", raw_llm)

        if try_cnt == MAX_TRY - 1:
            valid, res = extract_res_last_time(raw_llm) 
        else:
            valid, res = extract_res(raw_llm) 

        print("* res:", res)
        if valid:
            for pattern in res:
                all_mutators.append(pattern)
        # print("valid:", valid)

        if valid:
            SUCCESS = 1
            break
        else:
            dialog.append(
                {"role": "assistant", "content": raw_llm}
            )
            dialog.append(
                {"role": "user", "content": res + " \nPlease generate again."}
            )

        try_cnt += 1
    
    if SUCCESS:
        return res
    else:
        print("---- Can not finish this task. Here are the unsloved problem:", res)
        return None



if __name__ == "__main__":


    features = ["OP_REQUIRES"]
    features = ["TORCH_CHECK"]


    ############# Unit test

    # path = './testcpp/test.cpp'
    # path = "/Users/beimingyouyu/Desktop/CODES/pytorch-main/aten/src/ATen/native/AdaptiveAveragePooling.cpp"
    # analyze_cpp_file_main(path, features)
    # exit(0)



    ############# Formal use

    target_directory = '/Users/beimingyouyu/Desktop/CODES/pytorch-main/aten/src/ATen/native'

    
    sketelon_database = []
    res = []
    check_id = [0]
    cpp_files = find_cpp_files(target_directory)
    for cpp_file in cpp_files:
        print("\n\n[[cpp_file]]:", cpp_file)
        check_codes = analyze_cpp_file_main(cpp_file, features, sketelon_database, check_id)
        if check_codes:
            res.extend(check_codes)

    print(len(res))

    print("\n\n===== sketelon_database start =====")
    for tmp in sketelon_database:
        print(tmp)
    print("sketelon_database num:", len(sketelon_database))
    print("===== sketelon_database end =====\n\n")

    print("\n\n===== codes start =====")
    for tmp in res:
        print(tmp)
    print("codes num:", len(res))
    print("===== codes end =====\n\n")

    print("\n\n===== Prompt Start =====\n\n")
    with open('template.txt', 'r') as file:
        prompt_template = file.read()
    prompts = []
    for target_code in res:
        target_code = "".join(target_code)
        prompt = prompt_template.replace("<TARGET_CODE>", target_code)
        prompt = prompt.replace("<CHECK_FEATURE>", "TORCH_CHECK")
        prompts.append(prompt)


    messages_template = [
        {"role": "system", "content": "You are a coding expert."},
        {"role": "user", "content": ""}
    ]

    print("\n\n===== prompts start =====")
    all_mutators = []
    for prompt in tqdm(prompts, desc="Processing", unit="item"):
        print("\n------- prompt start --------")
        print(prompt)
        print("------- prompt end --------\n")

        print("\n------- reponse start --------")
        messages = messages_gen(prompt, messages_template)

        # reponse = request_openai_api(messages)
        # print(reponse)
        # extract_res(reponse.replace('\\"', ''))

        reask(messages, extract_res, 3, all_mutators)
        
        print("------- reponse end --------\n")
    print("===== prompts end =====\n\n")

    print("repeated_item:", repeated_item)

    filename = "all_mutators.json"
    with open(filename, 'w') as f:
        json.dump(all_mutators, f, indent=4)
    
