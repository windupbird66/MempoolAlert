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

# 加载 config.env 文件中的环境变量
load_dotenv('config.env')

# 全局变量用于控制程序运行和信号处理
running = True

def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    global running
    logging.info("\n正在停止程序...")
    running = False
    # 在接收到信号时尝试退出 Selenium WebDriver，如果已经初始化的话
    # WebDriver cleanup is also handled in the main try...finally block
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

def automate_minting_steps(private_key, receive_address, gas_fee_rate, keep_browser_open=False):
    """使用Selenium执行铸造的自动化步骤"""
    
    driver = None
    try:
        # 初始化 WebDriver
        # 如果使用了 Options 和 Service，请将它们作为参数传入
        # driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("正在初始化 WebDriver...")
        driver = webdriver.Chrome() # 假设 ChromeDriver 在 PATH 中
        logging.info("WebDriver 初始化成功")
        
        # 导航到目标网页
        url = "https://alkanes.ybot.io/?runeid=2:21568"
        logging.info(f"导航到网页: {url}")
        driver.get(url)
        logging.info("网页加载中...")
        
        # 等待页面加载 (可以根据实际情况调整等待时间或使用显式等待)
        time.sleep(5) 
        logging.info("网页加载完成，开始查找元素...")
        
        # 查找并填写私钥 (使用 ID 定位)
        try:
            logging.info("正在查找私钥输入框...")
            private_key_input = driver.find_element(By.ID, "wif")
            logging.info("找到私钥输入框，正在填写私钥...")
            private_key_input.send_keys(private_key)
            logging.info("私钥输入成功")
        except Exception as e:
            logging.error(f"查找或填写私钥失败 (ID='wif'): {e}")
            # 如果找不到私钥输入框，程序会继续，但后续步骤会失败
            
        # 查找并填写GAS费率 (使用 ID 定位)
        try:
            # 查找GAS费率输入框
            logging.info("正在查找GAS费率输入框...")
            gas_rate_input = driver.find_element(By.ID, "feeRate")
            logging.info(f"找到GAS费率输入框，正在清空并填写 {gas_fee_rate}...")
            gas_rate_input.clear()
            gas_rate_input.send_keys(str(gas_fee_rate)) # 确保输入的是字符串
            logging.info(f"GAS费率设置为 {gas_fee_rate}")
        except Exception as e:
            logging.error(f"查找或填写GAS费率失败 (ID='feeRate'): {e}")

        # 查找并填写铸造收货地址 (使用 ID 定位)
        if receive_address:
            try:
                logging.info("正在查找铸造收货地址输入框...")
                receive_address_input = driver.find_element(By.ID, "singleReceiveAddress")
                logging.info("找到铸造收货地址输入框，正在填写...")
                receive_address_input.clear() # 清空原有内容，如果需要
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
            logging.info("找到 '查询矿工钱包可Mint数量' 按钮，正在点击...")
            check_mintable_button.click()
            logging.info("点击 '查询矿工钱包可Mint数量' 按钮成功")
            
            # 使用显式等待等待查询结果出现
            try:
                logging.info("等待查询结果出现...")
                # 等待 id 为 'mintableResult' 的元素可见（可以根据实际情况调整等待时间）
                wait = WebDriverWait(driver, 20) # 增加等待时间以防网络延迟
                mintable_result_div = wait.until(EC.visibility_of_element_located((By.ID, "mintableResult")))
                logging.info("查询结果出现，自动化继续。")
            except Exception as e:
                logging.error(f"等待查询结果超时或出现错误: {e}")
                # 如果等待超时，后续步骤可能会失败，这里可以选择是否中断

        except Exception as e:
            logging.error(f"查找或点击 '查询矿工钱包可Mint数量' 按钮失败 (ID='checkMintable'): {e}")

        # 查找并点击"开始铸造"按钮
        try:
            logging.info("正在查找 '开始铸造' 按钮...")
            start_minting_button = driver.find_element(By.ID, "startMinting")
            logging.info("找到 '开始铸造' 按钮，正在点击...")
            start_minting_button.click()
            logging.info("点击 '开始铸造' 按钮成功")
            
            # 等待确认模态框出现并点击"确认"按钮
            try:
                logging.info("等待确认模态框出现...")
                # 使用显式等待等待模态框出现，或者等待确认按钮可点击
                wait = WebDriverWait(driver, 10)
                confirm_button = wait.until(EC.visibility_of_element_located((By.ID, "confirmMintButton")))
                
                logging.info("找到确认按钮，正在点击...")
                confirm_button.click()
                logging.info("点击确认按钮成功")
                
            except Exception as e:
                logging.error(f"处理确认模态框失败: {e}")

        except Exception as e:
             logging.error(f"查找或点击 '开始铸造' 按钮失败 (ID='startMinting'): {e}")
        
        # 在自动化完成后保持浏览器打开一段时间，方便检查 (可选)
        logging.info("自动化步骤完成。您可以检查浏览器状态。")
        if keep_browser_open:
             logging.info("根据设置，浏览器将保持开启。请手动关闭。")
             input("按 Enter 键关闭浏览器...") # 等待用户输入以保持浏览器开启
        
    except Exception as e:
        logging.error(f"自动化过程中发生错误: {e}")
    finally:
        # 关闭浏览器，除非 keep_browser_open 为 True
        if driver and not keep_browser_open:
            logging.info("正在关闭浏览器...")
            driver.quit()
            logging.info("浏览器已关闭")

def main():
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    
    logging.info("开始监控区块高度，目标区块: {}".format(TARGET_BLOCK_HEIGHT))
    
    # 检查是否提供了私钥、接收地址和 Gas 费率
    if YOUR_PRIVATE_KEY == 'YOUR_SECURELY_LOADED_PRIVATE_KEY_HERE':
        logging.error("请在 config.env 中设置 MINTER_PRIVATE_KEY 或在代码中安全加载私钥！")
        return # 不执行后续操作
    if not RECEIVE_ADDRESS:
        logging.error("请在 config.env 中设置 RECEIVE_ADDRESS！")
        return # 不执行后续操作
    if not GAS_FEE_RATE:
        logging.warning("未在 config.env 中设置 GAS_FEE_RATE，将使用默认值 3。")
        # 可以选择在这里设置默认值，或者在 os.getenv 中设置
        # GAS_FEE_RATE = '3' 
        
    try:
        while running:
            current_height = get_current_block_height()
            
            if current_height is not None:
                logging.info(f"当前区块高度: {current_height}")
                
                if current_height >= TARGET_BLOCK_HEIGHT:
                    logging.info(f"达到目标区块高度 {TARGET_BLOCK_HEIGHT}，开始执行自动化铸造步骤...")
                    # 确保将 Gas 费率转换为字符串传递给自动化函数
                    automate_minting_steps(YOUR_PRIVATE_KEY, RECEIVE_ADDRESS, str(GAS_FEE_RATE))
                    logging.info("自动化铸造步骤执行完毕。")
                    break # 自动化完成后退出循环
                else:
                    logging.info(f"距离目标区块还有 {TARGET_BLOCK_HEIGHT - current_height} 个区块")
            
            # 每5秒检查一次区块高度，同时检查 running 标志
            for _ in range(5):
                if not running:
                    break
                time.sleep(1)
        
    except KeyboardInterrupt:
        logging.info("\n程序被用户中断")
    except SystemExit:
        pass  # 忽略 SystemExit 异常，因为信号处理函数中已经处理
    finally:
        # 确保程序在退出时执行清理（如果需要）
        # Selenium WebDriver cleanup is primarily in automate_minting_steps' finally block
        logging.info("监控程序已停止。")

if __name__ == "__main__":
    main() 