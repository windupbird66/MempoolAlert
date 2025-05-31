import pygame
import time
import logging
import signal
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 全局变量用于控制循环
running = True

def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    global running
    logging.info("\n正在停止播放...")
    running = False

def test_sound():
    """测试音效播放"""
    try:
        # 设置信号处理
        signal.signal(signal.SIGINT, signal_handler)
        
        # 初始化pygame音频
        pygame.mixer.init()
        logging.info("正在初始化音频系统...")
        
        # 加载音频文件
        logging.info("正在加载音频文件 mempo.wav...")
        pygame.mixer.music.load('mempo.wav')
        
        # 设置循环播放
        pygame.mixer.music.play(-1)  # -1 表示无限循环
        logging.info("开始循环播放音频...")
        logging.info("按 Ctrl+C 停止播放")
        
        # 保持程序运行直到用户按下 Ctrl+C
        while running:
            pygame.time.Clock().tick(10)
            
    except Exception as e:
        logging.error(f"播放音频时出错: {str(e)}")
    finally:
        # 停止播放并清理资源
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        logging.info("音频播放已停止")

if __name__ == "__main__":
    test_sound() 