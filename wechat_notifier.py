import requests
import logging
import json
from typing import Dict

logger = logging.getLogger(__name__)

class WeChatNotifier:
    """微信推送类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.access_token = None
        self.token_expire_time = 0
    
    def get_access_token(self) -> str:
        """获取微信access_token"""
        import time
        
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
        
        if self.config.get('WECHAT_TEST'):
            appid = self.config.get('WECHAT_TEST_APPID')
            secret = self.config.get('WECHAT_TEST_SECRET')
        else:
            appid = self.config.get('WECHAT_APPID')
            secret = self.config.get('WECHAT_SECRET')
        
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                self.token_expire_time = time.time() + data.get('expires_in', 7200) - 300
                logger.info("获取微信access_token成功")
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                return ''
        except Exception as e:
            logger.error(f"获取access_token异常: {str(e)}")
            return ''
    
    def send_text_message(self, content: str) -> bool:
        """发送文本消息"""
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        try:
            if self.config.get('WECHAT_TEST'):
                url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
                touser = self.config.get('WECHAT_TEST_TOUSER')
                
                message = {
                    "touser": touser,
                    "msgtype": "text",
                    "text": {
                        "content": content[:1024]
                    }
                }
                
                response = requests.post(url, json=message, timeout=10)
                result = response.json()
                
                logger.info(f"消息发送结果: {result}")
                return result.get('errcode') == 0
            else:
                logger.info("正式号建议使用模板消息")
                return False
        except Exception as e:
            logger.error(f"发送微信消息异常: {str(e)}")
            return False
    
    def format_and_send(self, report: str) -> bool:
        return self.send_text_message(report)
    
    def send_news_report(self, title: str, content: str) -> bool:
        if self.config.get('WECHAT_TEST'):
            full_content = f"{title}\n\n{content}"
            return self.send_text_message(full_content)
        else:
            data = {
                "first": {"value": title, "color": "#173177"},
                "content": {"value": content[:500], "color": "#173177"},
                "remark": {"value": "\n点击查看详情", "color": "#173177"}
            }
            return self.send_template_message(data)
