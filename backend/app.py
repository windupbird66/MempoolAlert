from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import sys
import threading
import time
from database import db
import logging

# 定义后端服务器端口
BACKEND_PORT = 5000

app = Flask(__name__)
CORS(app) # 允许所有来源的跨域请求

@app.route('/user/login', methods=['POST'])
def user_login():
    """用户登录"""
    data = request.json
    address = data.get('address')
    
    if not address:
        return jsonify({'status': 'error', 'message': '缺少地址参数'}), 400

    try:
        # 验证地址是否允许访问
        if not db.is_address_allowed(address):
            return jsonify({'status': 'error', 'message': '该地址未被授权访问'}), 403

        # 创建或更新用户
        db.create_or_update_user(address)
        user = db.get_user(address)
        
        return jsonify({
            'status': 'success',
            'message': '登录成功',
            'user': user
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'登录失败: {str(e)}'}), 500

@app.route('/user/info', methods=['GET'])
def get_user_info():
    """获取用户信息"""
    address = request.args.get('address')
    if not address:
        return jsonify({'status': 'error', 'message': '缺少地址参数'}), 400

    try:
        user = db.get_user(address)
        if not user:
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404

        return jsonify({
            'status': 'success',
            'user': user
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取用户信息失败: {str(e)}'}), 500

@app.route('/user/deactivate', methods=['POST'])
def deactivate_user():
    """停用用户"""
    data = request.json
    address = data.get('address')
    
    if not address:
        return jsonify({'status': 'error', 'message': '缺少地址参数'}), 400

    try:
        db.deactivate_user(address)
        return jsonify({
            'status': 'success',
            'message': '用户已停用'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'停用用户失败: {str(e)}'}), 500

@app.route('/users', methods=['GET'])
def get_all_users():
    """获取所有用户"""
    try:
        users = db.get_all_users()
        return jsonify({
            'status': 'success',
            'users': users
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取用户列表失败: {str(e)}'}), 500

@app.route('/start_mint', methods=['POST'])
def start_mint():
    data = request.json
    private_key = data.get('private_key')
    receive_address = data.get('receive_address')
    gas_fee_rate = data.get('gas_fee_rate')
    target_block_height = data.get('target_block_height')
    client_address = data.get('client_address')

    if not all([private_key, receive_address, gas_fee_rate, target_block_height, client_address]):
        return jsonify({'status': 'error', 'message': '缺少必要的参数'}), 400

    try:
        # 验证用户是否存在且处于活动状态
        user = db.get_user(client_address)
        if not user:
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404
        if not user['is_active']:
            return jsonify({'status': 'error', 'message': '用户已被停用'}), 403

        target_block_height = int(target_block_height)
        gas_fee_rate = float(gas_fee_rate)
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': '目标区块高度或Gas费率格式错误'}), 400

    # 检查是否已存在该目标区块高度的任务
    existing_task = db.get_task_by_block_height(target_block_height)

    if existing_task:
        # 如果存在任务，先删除它
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE target_block_height = ?', (target_block_height,))
            conn.commit()
        logging.info(f"已删除目标区块 {target_block_height} 的旧任务")

    # 创建新任务
    # 构建运行mint_automation.py的命令
    mint_script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'mint_automation.py')
    project_root = os.path.dirname(os.path.dirname(__file__))

    command = [
        sys.executable,
        mint_script_path,
        private_key,
        receive_address,
        str(gas_fee_rate),
        str(target_block_height)
    ]

    # 使用subprocess启动任务
    process = subprocess.Popen(command, cwd=project_root)

    # 在数据库中创建新任务
    db.create_task(target_block_height, client_address, private_key, receive_address, gas_fee_rate)

    # 不再保存用户配置
    # db.save_user_config(client_address, private_key, receive_address, gas_fee_rate)

    return jsonify({
        'status': 'success',
        'message': f'目标区块 {target_block_height} 的铸造任务已启动'
    }), 200

@app.route('/tasks', methods=['GET'])
def get_tasks():
    client_address = request.args.get('address')
    if not client_address:
        return jsonify({'status': 'error', 'message': '缺少地址参数'}), 400

    # 验证用户是否存在且处于活动状态
    user = db.get_user(client_address)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    if not user['is_active']:
        return jsonify({'status': 'error', 'message': '用户已被停用'}), 403

    # 从数据库获取用户任务
    tasks = db.get_user_tasks(client_address)
    
    # 格式化任务信息
    user_tasks = []
    for task in tasks:
        task_status = {
            'target_block': task[0],
            'status': task[1],
            'start_time': task[2],
            'end_time': task[3]
        }
        user_tasks.append(task_status)

    return jsonify({'status': 'success', 'tasks': user_tasks}), 200

@app.route('/cancel_mint', methods=['POST'])
def cancel_mint():
    data = request.json
    target_block_height = data.get('target_block_height')
    client_address = data.get('client_address')

    if not all([target_block_height, client_address]):
        return jsonify({'status': 'error', 'message': '缺少必要的参数'}), 400

    try:
        # 验证用户是否存在且处于活动状态
        user = db.get_user(client_address)
        if not user:
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404
        if not user['is_active']:
            return jsonify({'status': 'error', 'message': '用户已被停用'}), 403

        # 更新任务状态为cancelling
        db.update_task_status(target_block_height, 'cancelling')
        return jsonify({
            'status': 'success',
            'message': f'目标区块 {target_block_height} 的铸造任务已标记为取消'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'取消任务失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=BACKEND_PORT) 