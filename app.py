from flask import Flask, request
import requests
import csv
import time
import json
import datetime
import re

app = Flask(__name__)

# 保存日志到CSV文件
def write_to_csv(client_ip,request_time, request_method, request_url, request_body, response_time, response_body,response_status,modified_response_body):
    # 获取当前日期
    current_date = datetime.datetime.now()

    # 获取当前日期所在年份和月份
    year = current_date.strftime('%Y')
    month = current_date.strftime('%m')

    # 格式化成所需的日期字符串
    log_file = f"log-{year}-{month}.csv"

    request_body = request_body.replace('\n', '')

    if response_status > 0:
        with open(log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([client_ip,request_time, request_method, request_url, request_body, response_time, response_body, response_status,  modified_response_body])

# 修改 JSON 中的内容
def modify_json(response_body):
    try:
        json_data = json.loads(response_body)
        message = json_data.get('message', {})
        content = message.get('content', '')

        modified_content = re.sub(r'\*[^*]*\*|\[[^\]]*\]|\([^)]*\)', '', content)
        
	# 更新 JSON 数据中的内容
        message['content'] = modified_content
        json_data['message'] = message
        return json.dumps(json_data, ensure_ascii=False)
    except json.JSONDecodeError:
        return response_body

# 定义目标域名
target_domain = "http://127.0.0.1:11434"

@app.route('/api/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    request_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    request_method = request.method
    request_url = request.url
    request_body = request.get_data(as_text=True)  # 获取请求数据体
    client_ip = request.remote_addr  # 获取客户端IP地址

    # 获取请求头
    headers = {key: value for (key, value) in request.headers}

    # 构建目标 URL
    url = f"{target_domain}/api/{path}"
    # print(request_body)   

    # 转发请求
    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        params=request.args.to_dict(),
        cookies=request.cookies
    )

    response_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    response_status = response.status_code
    response_body = response.content.decode('utf-8')  # 获取响应数据体
    # 记录请求和响应日志到CSV文件
    # print(response.content)

    # 修改 JSON 中的内容
    modified_response_body = modify_json(response_body)

    write_to_csv(client_ip,request_time, request_method, request_url, request_body, response_time, response_body, response_status, modified_response_body )

    # 返回响应
    return modified_response_body, response_status, response.headers.items()

