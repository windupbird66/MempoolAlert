import sqlite3
import json
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Database:
    def __init__(self, db_path='data/mempool.db'):
        # 确保data目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建允许地址表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS allowed_addresses (
                    address TEXT PRIMARY KEY,
                    description TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    added_by TEXT,
                    is_active BOOLEAN DEFAULT true
                )
            ''')

            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    address TEXT PRIMARY KEY,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建mint状态表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mint_status (
                    block_height INTEGER PRIMARY KEY,
                    status BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_block_height INTEGER,
                    client_address TEXT,
                    private_key TEXT,
                    receive_address TEXT,
                    gas_fee_rate REAL,
                    status TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_address) REFERENCES users(address)
                )
            ''')

            # 创建用户配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_configs (
                    address TEXT PRIMARY KEY,
                    private_key TEXT,
                    receive_address TEXT,
                    gas_fee_rate REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (address) REFERENCES users(address)
                )
            ''')

            # 初始化允许的地址
            self._init_allowed_addresses(cursor)

    def _init_allowed_addresses(self, cursor):
        """初始化允许的地址"""
        # 检查是否已经有数据
        cursor.execute('SELECT COUNT(*) FROM allowed_addresses')
        if cursor.fetchone()[0] == 0:
            # 添加默认允许的地址
            default_addresses = [
                ('bc1pz2lgnaugafuqqzaunjx8s0gthqc0vh9e', '默认地址1'),
                ('bc1pvquj09d3xj3ddkay555vrjuewh3k0q8d3gxh', '默认地址2'),
                ('bc1p56tzcefxuzgala27wcp4fxrw2e28wh9sz8up94', '默认地址3')
            ]
            cursor.executemany('''
                INSERT INTO allowed_addresses (address, description)
                VALUES (?, ?)
            ''', default_addresses)

    def is_address_allowed(self, address):
        """检查地址是否允许访问"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT is_active FROM allowed_addresses 
                WHERE address = ?
            ''', (address,))
            result = cursor.fetchone()
            return result[0] if result else False

    def add_allowed_address(self, address, description, added_by):
        """添加允许的地址"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO allowed_addresses (address, description, added_by)
                VALUES (?, ?, ?)
            ''', (address, description, added_by))
            conn.commit()

    def remove_allowed_address(self, address):
        """移除允许的地址（软删除）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE allowed_addresses 
                SET is_active = false
                WHERE address = ?
            ''', (address,))
            conn.commit()

    def get_allowed_addresses(self):
        """获取所有允许的地址"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT address, description, added_at, added_by, is_active
                FROM allowed_addresses
                ORDER BY added_at DESC
            ''')
            addresses = []
            for row in cursor.fetchall():
                addresses.append({
                    'address': row[0],
                    'description': row[1],
                    'added_at': row[2],
                    'added_by': row[3],
                    'is_active': row[4]
                })
            return addresses

    def create_or_update_user(self, address):
        """创建或更新用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (address, last_login, is_active)
                VALUES (?, ?, true)
                ON CONFLICT(address) DO UPDATE SET
                    last_login = ?,
                    is_active = true
            ''', (address, datetime.now(), datetime.now()))
            conn.commit()

    def get_user(self, address):
        """获取用户信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT address, last_login, is_active, created_at
                FROM users
                WHERE address = ?
            ''', (address,))
            result = cursor.fetchone()
            if result:
                return {
                    'address': result[0],
                    'last_login': result[1],
                    'is_active': result[2],
                    'created_at': result[3]
                }
            return None

    def deactivate_user(self, address):
        """停用用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users
                SET is_active = false
                WHERE address = ?
            ''', (address,))
            conn.commit()

    def get_all_users(self):
        """获取所有用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT address, last_login, is_active, created_at
                FROM users
                ORDER BY last_login DESC
            ''')
            users = []
            for row in cursor.fetchall():
                users.append({
                    'address': row[0],
                    'last_login': row[1],
                    'is_active': row[2],
                    'created_at': row[3]
                })
            return users

    def save_mint_status(self, block_height, status):
        """保存mint状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO mint_status (block_height, status, created_at)
                VALUES (?, ?, ?)
            ''', (block_height, status, datetime.now()))
            conn.commit()

    def check_mint_status(self, block_height):
        """检查mint状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT status FROM mint_status WHERE block_height = ?
            ''', (block_height,))
            result = cursor.fetchone()
            return result[0] if result else None

    def create_task(self, target_block_height, client_address, private_key, receive_address, gas_fee_rate):
        """创建新任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks 
                (target_block_height, client_address, private_key, receive_address, gas_fee_rate, status, start_time)
                VALUES (?, ?, ?, ?, ?, 'running', ?)
            ''', (target_block_height, client_address, private_key, receive_address, gas_fee_rate, datetime.now()))
            conn.commit()

    def update_task_status(self, target_block_height, status):
        """更新任务状态"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tasks 
                    SET status = ?, end_time = ?
                    WHERE target_block_height = ? AND status = 'running'
                ''', (status, datetime.now(), target_block_height))
                conn.commit()
                logging.info(f"任务 {target_block_height} 状态已更新为 {status}")
        except Exception as e:
            logging.error(f"更新任务状态失败: {e}")
            conn.rollback()

    def get_user_tasks(self, client_address):
        """获取用户的任务列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT target_block_height, status, start_time, end_time
                FROM tasks
                WHERE client_address = ?
                ORDER BY start_time DESC
            ''', (client_address,))
            return cursor.fetchall()

    def save_user_config(self, address, private_key, receive_address, gas_fee_rate):
        """保存用户配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_configs 
                (address, private_key, receive_address, gas_fee_rate, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (address, private_key, receive_address, gas_fee_rate, datetime.now()))
            conn.commit()

    def get_user_config(self, address):
        """获取用户配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT private_key, receive_address, gas_fee_rate
                FROM user_configs
                WHERE address = ?
            ''', (address,))
            result = cursor.fetchone()
            if result:
                return {
                    'private_key': result[0],
                    'receive_address': result[1],
                    'gas_fee_rate': result[2]
                }
            return None

    def get_task_by_block_height(self, target_block_height):
        """根据目标区块高度获取任务信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, status FROM tasks WHERE target_block_height = ?",
                    (target_block_height,)
                )
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"获取任务信息失败: {e}")
            return None

# 创建全局数据库实例
db = Database() 