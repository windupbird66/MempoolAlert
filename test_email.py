from mempool_monitor import send_email_notification
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_real_email():
    """发送一封真实的测试邮件"""
    logging.info("开始发送测试邮件...")
    try:
        success = send_email_notification()
        if success:
            logging.info("测试邮件发送成功！请检查您的邮箱：hezhaoqian1@foxmail.com")
            return True
        else:
            logging.error("邮件发送失败")
            return False
    except Exception as e:
        logging.error(f"发送测试邮件失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_real_email()
    if not success:
        logging.error("测试失败，请检查错误信息") 