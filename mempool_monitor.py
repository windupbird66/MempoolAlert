import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
import logging
import os
from dotenv import load_dotenv
import pygame
import signal
import sys

# 加载环境变量
load_dotenv('config.env')

# 初始化pygame音频
pygame.mixer.init()

# 全局变量用于控制循环
running = True

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    global running
    logging.info("\n正在停止程序...")
    running = False
    try:
        # 立即停止音频播放
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except:
        pass  # 忽略清理时的错误
    sys.exit(0)  # 强制退出程序

# 从环境变量获取配置
TARGET_BLOCK_HEIGHT = int(os.getenv('TARGET_BLOCK_HEIGHT', '899130'))
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.qq.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'hezhaoqian1@foxmail.com')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', 'hezhaoqian1@foxmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

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
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], message.as_string())
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

def play_alert_sound():
    """循环播放提示音"""
    try:
        # 使用自定义提示音
        pygame.mixer.music.load('mempo.wav')
        # 设置循环播放
        pygame.mixer.music.play(-1)  # -1 表示无限循环
        logging.info("开始循环播放提示音...")
        logging.info("按 Ctrl+C 停止播放")
    except Exception as e:
        logging.error(f"播放提示音失败: {str(e)}")

def main():
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    
    logging.info("开始监控区块高度...")
    notification_sent = False

    try:
        while running and not notification_sent:
            current_height = get_current_block_height()
            
            if current_height is not None:
                logging.info(f"当前区块高度: {current_height}")
                
                if current_height >= TARGET_BLOCK_HEIGHT:
                    logging.info(f"达到目标区块高度 {TARGET_BLOCK_HEIGHT}")
                    send_email_notification()
                    play_alert_sound()
                    notification_sent = True
                else:
                    logging.info(f"距离目标区块还有 {TARGET_BLOCK_HEIGHT - current_height} 个区块")
            
            # 使用5秒的检查间隔
            for _ in range(5):  # 将5秒分成5个1秒
                if not running:
                    break
                time.sleep(1)
                
    except KeyboardInterrupt:
        logging.info("\n程序被用户中断")
    except SystemExit:
        pass  # 忽略系统退出异常
    finally:
        try:
            # 确保清理资源
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass  # 忽略清理时的错误
        logging.info("程序已停止")

if __name__ == "__main__":
    main() 