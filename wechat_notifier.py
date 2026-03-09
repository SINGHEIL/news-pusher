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
        
        # 检查token是否有效
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
        
        # 确定使用测试号还是正式号
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
                self.token_expire_time = time.time() + data.get('expires_in', 7200) - 300  # 提前5分钟过期
                logger.info("获取微信access_token成功")
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                return ''
                
        except Exception as e:
            logger.error(f"获取access_token异常: {str(e)}")
            return ''
    
    def send_template_message(self, data: Dict) -> bool:
        """发送模板消息"""
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
            
            # 确定接收者
            if self.config.get('WECHAT_TEST'):
                touser = self.config.get('WECHAT_TEST_TOUSER')
                template_id = ''  # 测试号可能不需要template_id
            else:
                touser = self.config.get('WECHAT_TOUSER')
                template_id = self.config.get('WECHAT_TEMPLATE_ID')
            
            message = {
                "touser": touser,
                "template_id": template_id,
                "data": data
            }
            
            response = requests.post(url, json=message, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info("微信模板消息发送成功")
                return True
            else:
                logger.error(f"微信模板消息发送失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"发送微信模板消息异常: {str(e)}")
            return False
    
    def send_text_message(self, content: str) -> bool:
        """发送文本消息（使用模板消息接口）"""
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        try:
            # 使用模板消息接口
            if self.config.get('WECHAT_TEST'):
                # 测试号使用模板消息
                url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
                touser = self.config.get('WECHAT_TEST_TOUSER')
                template_id = ''  # 测试号可能不需要特定模板
                
                # 截断内容，避免过长
                if len(content) > 200:
                    content = content[:200] + "..."
                
                message = {
                    "touser": touser,
                    "template_id": template_id,
                    "data": {
                        "content": {
                            "value": content,
                            "color": "#173177"
                        }
                    }
                }
                
                response = requests.post(url, json=message, timeout=10)
                result = response.json()
                
                # 如果模板消息失败，尝试使用其他方式
                if result.get('errcode') != 0:
                    logger.warning(f"模板消息失败: {result}")
                    # 尝试使用简单接口
                    return self._send_simple_message(access_token, touser, content)
                
                logger.info("微信消息发送成功")
                return True
                
            else:
                logger.info("正式号建议使用模板消息")
                return False
                
        except Exception as e:
            logger.error(f"发送微信消息异常: {str(e)}")
            return False
    
    def _send_simple_message(self, access_token: str, touser: str, content: str) -> bool:
        """发送简单消息"""
        try:
            # 使用客服消息接口（需要在用户48小时内互动过）
            url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
            
            message = {
                "touser": touser,
                "msgtype": "text",
                "text": {
                    "content": content[:1024]  # 限制长度
                }
            }
            
            response = requests.post(url, json=message, timeout=10)
            result = response.json()
            
            logger.info(f"简单消息发送结果: {result}")
            return result.get('errcode') == 0
            
        except Exception as e:
            logger.error(f"发送简单消息异常: {str(e)}")
            return False
    
    def format_and_send(self, report: str) -> bool:
        """格式化并发送推送"""
        # 直接发送文本消息
        return self.send_text_message(report)
    
    def send_news_report(self, title: str, content: str) -> bool:
        """发送新闻报告"""
        if self.config.get('WECHAT_TEST'):
            # 测试号发送文本消息
            full_content = f"{title}\n\n{content}"
            return self.send_text_message(full_content)
        else:
            # 正式号发送模板消息
            data = {
                "first": {
                    "value": title,
                    "color": "#173177"
                },
                "content": {
                    "value": content[:500],  # 限制长度
                    "color": "#173177"
                },
                "remark": {
                    "value": "\n点击查看详情",
                    "color": "#173177"
                }
            }
            return self.send_template_message(data)
