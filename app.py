from flask import Flask, request
from datetime import datetime

import requests
import csv
import json
import re
import pytz
import random

app = Flask(__name__)

timezone = pytz.timezone('Asia/Shanghai')

def write_to_csv(client_ip,request_time, request_method, request_url, request_body, response_time, response_body,response_status,modified_response_body):
  
    current_date = datetime.now(timezone)
    year = current_date.strftime('%Y')
    month = current_date.strftime('%m')
    log_file = f"log-{year}-{month}.csv"

    request_body = request_body.replace('\n', '')

    if response_status > 0:
        with open(log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([request_time, client_ip, request_method, request_url, request_body, response_time, response_body, response_status,  modified_response_body])

def split_and_combine(text):
    sentences = []
    current_sentence = ""
    for char in text:
        current_sentence += char
        if char in ['.', '?', '!']:
            sentences.append(current_sentence)
            current_sentence = ""
    
    if len(sentences) == 0:
        return text

    current_string = ""
    for sentence in sentences:
        current_string += sentence
        if len(current_string) >= 80: 
            break
    return current_string

def modify_response(response_body):
    try:
        json_data = json.loads(response_body)
        message = json_data.get('message', {})
        content = message.get('content', '')

        modified_content = re.sub(r"^[A-Za-z]+ \((.*?)\): ", '', content)
        modified_content = re.sub(r'\*[^*]*\*|\[[^\]]*\]|\([^)]*\)', '', modified_content)
        modified_content = re.sub(r'#\w+', '', modified_content)
        modified_content = modified_content.replace('"', '')

        # modified_content = split_and_combine(modified_content.strip())

        message['content'] = modified_content.strip()
        json_data['message'] = message
        return json.dumps(json_data, ensure_ascii=False)
    except json.JSONDecodeError:
        return response_body

def modify_request(request_body):
    try:
        json_data = json.loads(request_body)
        model = json_data.get('model', '')
        
        if model == "sienna":
            json_data['model'] = 'streamer_v1'

        #random_seed = random.randint(1, 1000)
        
        random_seed = 100
        options_dict = {"seed": random_seed }
        json_data["options"] = options_dict
        
        return json.dumps(json_data,ensure_ascii=False).encode('utf-8')
    except json.JSONDecodeError:
        return request_body


# 定义目标域名
target_domain = "http://127.0.0.1:11434"

@app.route('/api/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    request_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
    request_method = request.method
    request_url = request.url
    request_body = request.get_data(as_text=True)  # 获取请求数据体
    client_ip = request.remote_addr  # 获取客户端IP地址
    
    # 获取请求头
    headers = {key: value for (key, value) in request.headers}

    # 构建目标 URL
    url = f"{target_domain}/api/{path}"
    # print(request_body)   

    modified_request_body = modify_request(request_body)

    # 转发请求
    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=modified_request_body,
        params=request.args.to_dict(),
        cookies=request.cookies
    )

    response_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
    response_status = response.status_code
    response_body = response.content.decode('utf-8',errors='ignore')  # 获取响应数据体
    # 记录请求和响应日志到CSV文件

    # 修改 JSON 中的内容
    modified_response_body = modify_response(response_body)

    write_to_csv(client_ip,request_time, request_method, request_url,  request_body, response_time, response_body, response_status, modified_response_body )

    # 返回响应
    return modified_response_body, response_status, response.headers.items()

