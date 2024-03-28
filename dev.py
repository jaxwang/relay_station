from flask import Flask, request
import requests

app = Flask(__name__)

# 定义目标域名
target_domain = "http://127.0.0.1:11434"

@app.route('/api/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # 记录请求日志
    print(f"Received {request.method} request to {request.url}")
    print(request.get_data());
    # 获取请求头
    headers = {key: value for (key, value) in request.headers}

    # 构建目标 URL
    url = f"{target_domain}/api/{path}"

    print(request.get_data())
    # 转发请求
    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        params=request.args.to_dict(),
        cookies=request.cookies
    )
    # 记录响应日志
    print(f"Forwarded {request.method} request to {url}. Response: {response.status_code}")
    print(response.content)
    # 返回响应
    return response.content, response.status_code, response.headers.items()

if __name__ == '__main__':
    app.run(port=5000)
