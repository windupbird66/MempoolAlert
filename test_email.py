from mempool_monitor import send_email_notification, get_current_block_height
import logging
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_current_height_email():
    """发送当前区块高度的邮件"""
    logging.info("开始获取当前区块高度...")
    current_height = get_current_block_height()
    
    if current_height is None:
        logging.error("获取区块高度失败")
        return False
        
    logging.info(f"当前区块高度: {current_height}")
    
    # 修改邮件内容
    subject = "当前区块高度"
    content = f"当前区块高度为：{current_height}\n距离目标区块高度 899130 还有 {899130 - current_height} 个区块"
    
    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login("hezhaoqian1@foxmail.com", "wfwwxaycuzcldfhj")
            
            message = MIMEText(content, 'plain', 'utf-8')
            message['Subject'] = Header(subject, 'utf-8')
            message['From'] = "hezhaoqian1@foxmail.com"
            message['To'] = "hezhaoqian1@foxmail.com"
            
            server.sendmail("hezhaoqian1@foxmail.com", ["hezhaoqian1@foxmail.com"], message.as_string())
            try:
                server.quit()
            except:
                pass
                
        logging.info("邮件发送成功！请检查您的邮箱：hezhaoqian1@foxmail.com")
        return True
    except Exception as e:
        logging.error(f"发送邮件失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = send_current_height_email()
    if not success:
        logging.error("测试失败，请检查错误信息") 