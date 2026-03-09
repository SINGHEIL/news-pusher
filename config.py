import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置管理类"""
    
    # 推送时间
    PUSH_TIME = os.getenv('PUSH_TIME', '09:00')
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    
    # 微信配置
    WECHAT_APPID = os.getenv('WECHAT_APPID', '')
    WECHAT_SECRET = os.getenv('WECHAT_SECRET', '')
    WECHAT_TEMPLATE_ID = os.getenv('WECHAT_TEMPLATE_ID', '')
    WECHAT_TOUSER = os.getenv('WECHAT_TOUSER', '')
    
    # 测试号配置
    WECHAT_TEST = os.getenv('WECHAT_TEST', 'False').lower() == 'true'
    WECHAT_TEST_APPID = os.getenv('WECHAT_TEST_APPID', '')
    WECHAT_TEST_SECRET = os.getenv('WECHAT_TEST_SECRET', '')
    WECHAT_TEST_TOUSER = os.getenv('WECHAT_TEST_TOUSER', '')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
