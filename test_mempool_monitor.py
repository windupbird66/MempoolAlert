import unittest
from unittest.mock import patch, MagicMock
from mempool_monitor import get_current_block_height, send_email_notification

class TestMempoolMonitor(unittest.TestCase):
    
    @patch('requests.get')
    def test_get_current_block_height_success(self, mock_get):
        # 模拟成功的API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "899000"
        mock_get.return_value = mock_response
        
        result = get_current_block_height()
        self.assertEqual(result, 899000)
        
    @patch('requests.get')
    def test_get_current_block_height_failure(self, mock_get):
        # 模拟失败的API响应
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = get_current_block_height()
        self.assertIsNone(result)
    
    @patch('smtplib.SMTP')
    def test_send_email_notification(self, mock_smtp):
        # 模拟SMTP服务器
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # 测试发送邮件
        send_email_notification()
        
        # 验证SMTP服务器被正确调用
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

def run_tests():
    """运行所有测试"""
    print("开始运行测试...")
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests() 