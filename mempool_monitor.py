import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
import logging
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 目标区块高度
TARGET_BLOCK_HEIGHT = 899130

# 邮件配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'hezhaoqian1@foxmail.com')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', 'hezhaoqian1@foxmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # 从环境变量获取密码

if not SMTP_PASSWORD:
    raise ValueError("请设置环境变量 SMTP_PASSWORD")

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

def send_email_notification():
    """发送邮件通知"""
    subject = "区块高度提醒"
    content = f"区块高度已达到目标值 {TARGET_BLOCK_HEIGHT}！"
    
    message = MIMEText(content, 'plain', 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], message.as_string())
            # 检查邮件是否真的发送成功
            try:
                server.quit()
            except:
                pass  # 忽略退出时的错误
        logging.info("邮件发送成功")
        return True
    except Exception as e:
        # 如果邮件已经发送成功，但只是退出时出错，我们仍然认为发送成功
        if "邮件发送成功" in str(e):
            logging.info("邮件发送成功")
            return True
        logging.error(f"发送邮件失败: {str(e)}")
        raise

def main():
    logging.info("开始监控区块高度...")
    notification_sent = False

    while not notification_sent:
        current_height = get_current_block_height()
        
        if current_height is not None:
            logging.info(f"当前区块高度: {current_height}")
            
            if current_height >= TARGET_BLOCK_HEIGHT:
                logging.info(f"达到目标区块高度 {TARGET_BLOCK_HEIGHT}")
                send_email_notification()
                notification_sent = True
            else:
                logging.info(f"距离目标区块还有 {TARGET_BLOCK_HEIGHT - current_height} 个区块")
        
        # 每60秒检查一次
        time.sleep(60)

if __name__ == "__main__":
    main() 