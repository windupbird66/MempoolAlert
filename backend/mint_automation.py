import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
import os
from dotenv import load_dotenv
import requests
import signal
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pygame
from database import db
from selenium.common.exceptions import TimeoutException

# 加载 config.env 文件中的环境变量
# 假设 config.env 在项目根目录下的 config 文件夹中
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.env')
load_dotenv(config_path)

# 全局变量用于控制程序运行和信号处理
running = True

# mint状态文件路径
# 假设 mint_status.json 在项目根目录下的 data 文件夹中
MINT_STATUS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'mint_status.json')

def load_mint_status():
    """从文件加载mint状态"""
    if os.path.exists(MINT_STATUS_FILE):
        try:
            with open(MINT_STATUS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"加载mint状态文件失败: {e}")
    return {}

def save_mint_status(block_height, status):
    """保存mint状态"""
    db.save_mint_status(block_height, status)

def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    global running
    logging.info("\n正在停止程序...")
    running = False
    try:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except:
        pass
    sys.exit(0)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 从环境变量获取配置
TARGET_BLOCK_HEIGHT = int(os.getenv('TARGET_BLOCK_HEIGHT', '899130'))

# IMPORTANT: Load your private key, receive address, and gas rate securely from config.env
YOUR_PRIVATE_KEY = os.getenv('MINTER_PRIVATE_KEY', 'YOUR_SECURELY_LOADED_PRIVATE_KEY_HERE') # <-- 确保这里与 config.env 中的键一致
RECEIVE_ADDRESS = os.getenv('RECEIVE_ADDRESS', '')
GAS_FEE_RATE = os.getenv('GAS_FEE_RATE', '3') # 从环境变量获取 Gas 费率，默认为 3

def get_current_block_height():
    """获取当前区块高度"""
    try:
        response = requests.get("https://mempool.space/api/blocks/tip/height")
        if response.status_code == 200:
            return int(response.text)
        else:
            logging.error(f"获取区块高度失败: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"请求出错: {str(e)}")
        return None

class MintAutomation:
    def __init__(self, private_key, receive_address, gas_fee_rate):
        self.private_key = private_key
        self.receive_address = receive_address
        self.gas_fee_rate = gas_fee_rate
        
        # 配置 Chrome Options
        options = Options()
        options.add_argument('--headless')  # 启用无头模式
        options.add_argument('--no-sandbox') # 解决在某些 Linux 环境下的权限问题
        options.add_argument('--disable-dev-shm-usage') # 解决 /dev/shm 空间不足的问题
        
        # 初始化 WebDriver，并传入 Options
        logging.info("正在初始化 WebDriver (无头模式)...")
        self.driver = webdriver.Chrome(options=options)
        logging.info("WebDriver 初始化成功")

    def __del__(self):
        """确保在对象销毁时关闭 WebDriver"""
        if self.driver:
            logging.info("正在关闭 WebDriver...")
            self.driver.quit()
            logging.info("WebDriver 已关闭")

    def wait_for_confirm_modal(self):
        """等待确认模态框出现并点击"确认"按钮"""
        try:
            logging.info("等待确认模态框出现...")
            wait = WebDriverWait(self.driver, 20)
            
            # 等待确认按钮出现并可点击
            logging.info("等待确认按钮出现...")
            confirm_button = wait.until(
                EC.element_to_be_clickable((By.ID, "confirmMintButton"))
            )
            
            # 打印确认按钮的文本内容
            logging.info(f"确认按钮文本: {confirm_button.text}")
            
            # 确保按钮在视图中
            self.driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
            time.sleep(1)
            
            logging.info("找到确认按钮，正在点击...")
            # 使用 JavaScript 点击按钮
            self.driver.execute_script("arguments[0].click();", confirm_button)
            logging.info("点击确认按钮成功")
            
            # 等待确认操作完成
            logging.info("等待订单提交完成...")
            try:
                wait = WebDriverWait(self.driver, 60)
                wait.until(EC.invisibility_of_element_located((By.ID, "waitingModal")))
                logging.info("订单提交完成，等待模态框已关闭")
            except Exception as e:
                logging.warning(f"等待订单提交完成时超时: {e}")
            
            time.sleep(3)
            logging.info("所有操作完成")
            
        except Exception as e:
            logging.error(f"处理确认模态框失败: {e}")

def automate_minting_steps(private_key, receive_address, gas_fee_rate, keep_browser_open=False):
    """使用Selenium执行铸造的自动化步骤"""
    
    driver = None
    try:
        # 初始化 WebDriver
        logging.info("正在初始化 WebDriver...")
        driver = webdriver.Chrome()
        logging.info("WebDriver 初始化成功")
        
        # 导航到目标网页
        url = "https://alkanes.ybot.io/?runeid=2:21568"
        logging.info(f"导航到网页: {url}")
        driver.get(url)
        logging.info("网页加载中...")
        
        # 等待页面加载
        time.sleep(3)
        logging.info("网页加载完成，开始查找元素...")
        
        # 查找并填写私钥
        try:
            logging.info("正在查找私钥输入框...")
            private_key_input = driver.find_element(By.ID, "wif")
            logging.info("找到私钥输入框，正在填写私钥...")
            private_key_input.send_keys(private_key)
            logging.info("私钥输入成功")
        except Exception as e:
            logging.error(f"查找或填写私钥失败 (ID='wif'): {e}")
            
        # 查找并填写GAS费率
        try:
            logging.info("正在查找GAS费率输入框...")
            gas_rate_input = driver.find_element(By.ID, "feeRate")
            logging.info(f"找到GAS费率输入框，正在清空并填写 {gas_fee_rate}...")
            gas_rate_input.clear()
            gas_rate_input.send_keys(str(gas_fee_rate))
            logging.info(f"GAS费率设置为 {gas_fee_rate}")
        except Exception as e:
            logging.error(f"查找或填写GAS费率失败 (ID='feeRate'): {e}")

        # 查找并填写铸造收货地址
        if receive_address:
            try:
                logging.info("正在查找铸造收货地址输入框...")
                receive_address_input = driver.find_element(By.ID, "singleReceiveAddress")
                logging.info("找到铸造收货地址输入框，正在填写...")
                receive_address_input.clear()
                receive_address_input.send_keys(receive_address)
                logging.info("铸造收货地址填写成功")
            except Exception as e:
                logging.error(f"查找或填写铸造收货地址失败 (ID='singleReceiveAddress'): {e}")
        else:
            logging.warning("未提供铸造收货地址 (RECEIVE_ADDRESS)，跳过填写。")
            
        # 查找并点击"查询矿工钱包可Mint数量"按钮
        try:
            logging.info("正在查找 '查询矿工钱包可Mint数量' 按钮...")
            check_mintable_button = driver.find_element(By.ID, "checkMintable")
            
            # 滚动到按钮位置并等待
            driver.execute_script("arguments[0].scrollIntoView(true);", check_mintable_button)
            time.sleep(2)
            
            logging.info("找到 '查询矿工钱包可Mint数量' 按钮，正在点击...")
            # 使用 JavaScript 点击按钮
            driver.execute_script("arguments[0].click();", check_mintable_button)
            logging.info("点击 '查询矿工钱包可Mint数量' 按钮成功")
            
            # 等待查询结果出现
            try:
                logging.info("等待查询结果出现...")
                wait = WebDriverWait(driver, 20)
                mintable_result_div = wait.until(EC.visibility_of_element_located((By.ID, "mintableResult")))
                logging.info("查询结果出现，自动化继续。")
            except Exception as e:
                logging.error(f"等待查询结果超时或出现错误: {e}")

        except Exception as e:
            logging.error(f"查找或点击 '查询矿工钱包可Mint数量' 按钮失败 (ID='checkMintable'): {e}")

        # 查找并点击"开始铸造"按钮
        try:
            logging.info("正在查找 '开始铸造' 按钮...")
            start_minting_button = driver.find_element(By.ID, "startMinting")
            
            # 滚动到按钮位置并等待
            driver.execute_script("arguments[0].scrollIntoView(true);", start_minting_button)
            time.sleep(2)
            
            logging.info("找到 '开始铸造' 按钮，正在点击...")
            # 使用 JavaScript 点击按钮
            driver.execute_script("arguments[0].click();", start_minting_button)
            logging.info("点击 '开始铸造' 按钮成功")
            
            # 等待确认模态框出现并点击"确认"按钮
            try:
                logging.info("等待确认模态框出现...")
                wait = WebDriverWait(driver, 20)
                
                # 等待确认按钮出现并可点击
                logging.info("等待确认按钮出现...")
                confirm_button = wait.until(
                    EC.element_to_be_clickable((By.ID, "confirmMintButton"))
                )
                
                # 打印确认按钮的文本内容
                logging.info(f"确认按钮文本: {confirm_button.text}")
                
                # 确保按钮在视图中
                driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
                time.sleep(1)
                
                logging.info("找到确认按钮，正在点击...")
                # 使用 JavaScript 点击按钮
                driver.execute_script("arguments[0].click();", confirm_button)
                logging.info("点击确认按钮成功")
                
                # 等待确认操作完成
                logging.info("等待订单提交完成...")
                try:
                    wait = WebDriverWait(driver, 60)
                    wait.until(EC.invisibility_of_element_located((By.ID, "waitingModal")))
                    logging.info("订单提交完成，等待模态框已关闭")
                except Exception as e:
                    logging.warning(f"等待订单提交完成时超时: {e}")
                
                time.sleep(3)
                logging.info("所有操作完成")
                
            except Exception as e:
                logging.error(f"处理确认模态框失败: {e}")

        except Exception as e:
            logging.error(f"查找或点击 '开始铸造' 按钮失败 (ID='startMinting'): {e}")
        
        logging.info("自动化步骤完成。您可以检查浏览器状态。")
        if keep_browser_open:
            logging.info("根据设置，浏览器将保持开启。请手动关闭。")
            input("按 Enter 键关闭浏览器...")
        
    except Exception as e:
        logging.error(f"自动化过程中发生错误: {e}")
    finally:
        if driver and not keep_browser_open:
            logging.info("正在关闭浏览器...")
            driver.quit()
            logging.info("浏览器已关闭")

def play_alert_sound():
    """循环播放提示音"""
    try:
        # 使用自定义提示音
        # 假设 mempo.wav 在项目根目录下的 assets 文件夹中
        sound_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'mempo.wav')
        pygame.mixer.music.load(sound_file_path)
        # 设置循环播放
        pygame.mixer.music.play(-1)  # -1 表示无限循环
        logging.info("开始循环播放提示音...")
        logging.info("按 Ctrl+C 停止播放")
    except Exception as e:
        logging.error(f"播放提示音失败: {str(e)}")

def check_task_cancelled(target_block_height):
    """检查任务是否被取消"""
    try:
        # 从数据库获取任务状态
        task = db.get_task_by_block_height(target_block_height)
        if task and task[1] == 'cancelling':
            logging.info(f"任务 {target_block_height} 已被标记为取消")
            return True
        return False
    except Exception as e:
        logging.error(f"检查任务状态失败: {e}")
        return False

def main():
    if len(sys.argv) != 5:
        print("用法: python mint_automation.py <private_key> <receive_address> <gas_fee_rate> <target_block_height>")
        sys.exit(1)

    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 初始化 pygame
    pygame.mixer.init()

    # 获取命令行参数
    private_key = sys.argv[1]
    receive_address = sys.argv[2]
    gas_fee_rate = sys.argv[3]
    target_block_height = int(sys.argv[4])

    logging.info(f"目标区块高度: {target_block_height}")
    logging.info(f"接收地址: {receive_address}")
    logging.info(f"Gas 费率: {gas_fee_rate}")

    try:
        while running:
            current_height = get_current_block_height()
            if current_height is not None:
                logging.info(f"当前区块高度: {current_height}，目标区块: {target_block_height}")

                # 检查任务是否被取消
                if check_task_cancelled(target_block_height):
                    logging.info("任务已被取消，停止执行")
                    db.update_task_status(target_block_height, 'cancelled')
                    break

                if current_height >= target_block_height:
                    logging.info(f"已达到目标区块高度 {target_block_height}")
                    # 再次检查任务是否被取消
                    if check_task_cancelled(target_block_height):
                        logging.info("任务已被取消，停止执行")
                        db.update_task_status(target_block_height, 'cancelled')
                        break

                    # 执行铸造步骤
                    automate_minting_steps(private_key, receive_address, gas_fee_rate)
                    # 播放提示音
                    play_alert_sound()
                    # 更新任务状态为已完成
                    db.update_task_status(target_block_height, 'completed')
                    break
                elif current_height == target_block_height - 1:
                    logging.info(f"当前区块 {current_height}，下一个区块 {target_block_height} 将是目标区块，开始执行自动化铸造步骤...")
                    # 执行铸造步骤
                    automate_minting_steps(private_key, receive_address, gas_fee_rate)
                    # 播放提示音
                    play_alert_sound()
                    # 更新任务状态为已完成
                    db.update_task_status(target_block_height, 'completed')
                    break

            # 每5秒检查一次
            for _ in range(5):
                if not running:
                    break
                time.sleep(1)

    except Exception as e:
        logging.error(f"程序执行出错: {e}")
        # 更新任务状态为失败
        db.update_task_status(target_block_height, 'failed')
    finally:
        # 清理资源
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass

if __name__ == "__main__":
    main() 