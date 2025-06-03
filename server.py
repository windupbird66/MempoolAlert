import http.server
import socketserver
import webbrowser
import os
import threading
import time
import requests
import sys
import subprocess

# 前端静态文件端口
FRONTEND_PORT = 8000
# 后端API端口 (与backend/app.py中设置的端口一致)
BACKEND_PORT = 5000
BACKEND_URL = f'http://localhost:{BACKEND_PORT}'

# 自定义HTTP请求处理程序
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    # 修改serve_forever的根目录为项目根目录
    def __init__(self, *args, **kwargs):
        # 使用当前工作目录作为静态文件服务的根目录
        super().__init__(*args, directory='.', **kwargs)

    def translate_path(self, path):
        # 将根路径 '/' 映射到 frontend/index.html
        if path == '/':
            path = '/frontend/index.html'
        # 其他路径交给父类处理
        return super().translate_path(path)

    def do_POST(self):
        # 检查是否是发送到后端API的请求
        if self.path == '/start_mint':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # 将请求转发到后端Flask应用
                backend_response = requests.post(BACKEND_URL + self.path, data=post_data, headers={'Content-Type': 'application/json'})
                
                # 将后端响应返回给前端
                self.send_response(backend_response.status_code)
                # 复制后端的所有头部，包括 Content-type
                for header, value in backend_response.headers.items():
                     self.send_header(header, value)
                # 确保允许跨域访问，即使后端没有设置
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(backend_response.content)
                
            except Exception as e:
                self.send_error(500, f'转发请求到后端失败: {e}')
        else:
            # 对于非/start_mint的POST请求，返回404
             self.send_error(404, 'File Not Found')

    def do_GET(self):
        # 处理静态文件请求 (例如 index.html, dashboard.html)
        # 允许跨域访问静态文件
        self.send_response(200) # 明确发送200 OK状态码
        self.send_header('Access-Control-Allow-Origin', '*') # 发送CORS头部
        # 让基类处理其余的头部和文件内容发送
        super().do_GET()

    # 允许OPTIONS请求，用于CORS预检
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def run_frontend_server():
    """运行前端静态文件服务器"""
    # 设置处理程序
    Handler = CustomHTTPRequestHandler

    # 创建服务器
    with socketserver.TCPServer(("", FRONTEND_PORT), Handler) as httpd:
        print(f"前端服务器已启动在 http://localhost:{FRONTEND_PORT}")
        print("请在浏览器中打开上述地址")
        print("按 Ctrl+C 可以停止服务器")

        # 自动打开浏览器
        webbrowser.open(f'http://localhost:{FRONTEND_PORT}/frontend/index.html')

        # 启动服务器
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n前端服务器已停止")

def run_backend_server():
    """运行后端Flask应用"""
    print(f"正在启动后端服务器在 http://localhost:{BACKEND_PORT}...")
    # 注意: 假设backend/app.py是可执行的
    # 可以在这里添加虚拟环境的路径，如果使用了虚拟环境
    backend_script_path = os.path.join(os.path.dirname(__file__), 'backend', 'app.py')
    command = [sys.executable, backend_script_path]
    try:
        # 使用subprocess.run，让backend在当前终端输出日志
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"后端服务器启动失败，错误码: {e.returncode}")
    except FileNotFoundError:
         print(f"错误: 未找到 backend/app.py 脚本在 {backend_script_path}")

if __name__ == '__main__':
    # 在新线程中启动后端服务器
    backend_thread = threading.Thread(target=run_backend_server)
    backend_thread.daemon = True # 设置为守护线程，主线程退出时它也会退出
    backend_thread.start()

    # 等待后端启动 (根据需要调整等待时间)
    time.sleep(5)

    # 在主线程中运行前端服务器
    run_frontend_server() 