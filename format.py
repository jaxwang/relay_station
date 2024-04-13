import csv
import json
import os
import sys
import subprocess

def csv_to_dict_set(file_path):
    with open(file_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        rows = list(reader)  # 将 reader 对象的内容存储在列表中

        with open('output/streamer_chat_records.jsonl', 'w') as jsonl_file:
            
            for current_line_num, row in enumerate(rows):
                data_set_line = {
                    "conversation_id": 0,
                    "category": "streamer_chatting",
                    "conversation": [],
                    "dataset": "streamer_chat_records"
                }
                data_set_line['conversation_id'] = current_line_num+1
                conversation = {"human": row["Question"], "assistant": row["Answer"]}
                data_set_line['conversation'] = [conversation]

                # 将字典转换为 JSON 格式并添加换行符
                json_data = json.dumps(data_set_line) + '\n'
                # print(json_data)
                # 将 JSON 字符串写入文件
                jsonl_file.write(json_data)

        with open('output/streamer_chat_records.json', 'w') as json_file:

            data_list = []

            for row in rows:
                data_single = {
                    "instruction" : "",
                    "input" : "",
                    "output" : "",
                    "history" : [],
                }
                data_single["instruction"] = row["Question"]
                data_single["output"] = row["Answer"]
                # print(data_single)
                data_list.append(data_single)

            json_data = json.dumps(data_list,indent=4)
            json_file.write(json_data)

def main():
    if len(sys.argv) > 1:
        csv_file=sys.argv[1]
        if not os.path.exists(csv_file): 
            print("该文件不存在, 请检查参数: "+ csv_file )
            sys.exit(1)
        elif not csv_file.endswith(".csv"):
            print("该文件不是CSV文件, 请检查参数: "+ csv_file )
            sys.exit(1)

        print("CSV文件路径为:"+csv_file)
    else:
        print("未传入CSV文件路径!")
        sys.exit(1)


    directory = "output"

    if not os.path.exists(directory): os.mkdir(directory)

    csv_to_dict_set(csv_file)
    result = subprocess.run("ls -lh output", shell=True, capture_output=True, text=True)
    print("已生成训练数据集文件:", result.stdout)

if __name__ == "__main__":
     main()
    