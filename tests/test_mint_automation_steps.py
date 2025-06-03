import os
from dotenv import load_dotenv
from backend import mint_automation # 更新导入路径
import logging
import unittest

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_automation_steps():
    """测试自动化铸造的Selenium步骤"""
    
    # 加载 config.env 文件中的环境变量
    load_dotenv('config.env')
    
    # 从环境变量获取私钥、接收地址和 Gas 费率
    # IMPORTANT: Load your private key securely from config.env
    YOUR_PRIVATE_KEY = os.getenv('MINTER_PRIVATE_KEY', 'YOUR_SECURELY_LOADED_PRIVATE_KEY_HERE') # <-- 确保这里与 config.env 中的键一致
    RECEIVE_ADDRESS = os.getenv('RECEIVE_ADDRESS', '')
    GAS_FEE_RATE = os.getenv('GAS_FEE_RATE', '3') # 从环境变量获取 Gas 费率，默认为 3

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

    logging.info("开始测试自动化铸造步骤...")
    
    # 调用 mint_automation.py 中的自动化函数，传入私钥、接收地址和 Gas 费率，并保持浏览器开启
    mint_automation.automate_minting_steps(YOUR_PRIVATE_KEY, RECEIVE_ADDRESS, str(GAS_FEE_RATE), keep_browser_open=True)
    
    logging.info("自动化铸造步骤测试完成。")

if __name__ == "__main__":
    test_automation_steps()

# 为了简单起见，先注释掉实际的测试代码，只更新导入

# if __name__ == '__main__':
#     unittest.main() 