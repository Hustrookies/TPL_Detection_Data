import os
import re
import json

def extract_profile_matches(file_path):
    profile_matches = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if "name" in lines[i]:
                name = re.search(r'name: (.*)', lines[i])
                version = re.search(r'version: ([\w.-]+)', lines[i+2])
                if name and version:
                    profile_matches.append([name.group(1).strip(), version.group(1).strip()])
    return profile_matches

def fuzzy_match(profile, lib):
    a1, b1 = profile
    a2, b2 = lib
    if a2 in a1 and b1 == b2:
        return True
    return False

def detection_vision(file_name, profile_matches, json_path):
    TP = 0
    FP = 0
    FN = 0
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
        for item in data:
            if item['name'] == file_name:
                # 对于每一个item，遍历其libraries，检查是否在profile_matches中
                for lib in item['libraries']:
                    is_FP = False
                    is_TP = False
                    for profile in profile_matches:
                         if fuzzy_match(profile,[lib['name'], lib['version']]):
                            is_TP = True
                            break
                         elif lib['name'] in profile[0]:
                            is_FP = True
                    if is_TP:
                        TP += 1
                    elif is_FP:
                        FP += 1
                    else:   
                        FN += 1   
                break

    return [TP, FP, FN]

def detection_lib(file_name, profile_matches, json_path):
    TP = 0
    FP = 0
    FN = 0
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
        for item in data:
            if item['name'] == file_name:
                # 对于每一个item，遍历其libraries，检查是否在profile_matches中
                for lib in item['libraries']:
                    is_TP = False
                    for profile in profile_matches:
                         if lib['name'] in profile[0]:
                            is_TP = True
                            break
                    if is_TP:
                        TP += 1
                    else:   
                        FN += 1   
                break
    #这里还要讨论一下
    FP = len(profile_matches) - TP
    if FP > 1:
        FP = 1
    return [TP, FP, FN]

def main():
    dir_path = "/home/lith/Libscout/LibScout/build/libs/logs"  # 替换为你的目录路径
    json_path = "/home/lith/data/gt/lib_truth_all.json"  # 替换为你的JSON文件路径
    TP = 0
    FP = 0
    FN = 0
    # 创建一个字典，将用户的输入映射到相应的文件后缀
    suffix_dict = {
        "1": "_srk.log",
        "2": "_obf.log",
        "3": "_opt-srk.log",
        "4": "_opt-obf-srk.log",
        "5": ".log"
    }

    # 打印可供选择的后缀信息，让用户选择
    print("Please choose the suffix of the log file:")
    print("1. _srk.log")
    print("2. _obf.log")
    print("3. _opt-srk.log")
    print("4. _opt-obf-srk.log")
    print("5. .log")

    # 获取用户的输入
    suffix_number = input("Please input the number of the suffix:")

    # 从字典中获取相应的文件后缀
    suffix = suffix_dict.get(suffix_number, " ")  # 如果用户输入的数字不在字典中，将使用默认值" "
      # 打印可供选择的检测方法，让用户选择
    print("Please choose the detection method:")
    print("1. detection_version")
    print("2. detection_lib")

    # 获取用户的输入
    detection_number = input("Please input the number of the detection method:")

    # 创建一个字典，将用户的输入映射到相应的检测方法
    detection_dict = {
        "1": detection_vision,
        "2": detection_lib
    }

    # 从字典中获取相应的检测方法
    detection_method = detection_dict.get(detection_number, detection_vision)  # 如果用户输入的数字不在字典中，将使用默认的检测方法detection_vision

    

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(suffix):
                file_path = os.path.join(root, file)
                file_name = os.path.splitext(file)[0]
                parts = file_name.split("_")
                if suffix_number=="5" and len(parts) > 1 :
                    continue
                file_name = parts[0]
                profile_matches = extract_profile_matches(file_path)
                print(f"File {file_name}: {profile_matches}")
                count = detection_method(file_name, profile_matches, json_path)
                print(f"File {file_name} has TP:{count[0]} FP:{count[1]} FN:{count[2]}")
                TP += count[0]
                FP += count[1]
                FN += count[2]
    print(f"TP:{TP} FP:{FP} FN:{FN}")
               

if __name__ == '__main__':
    main()
    

