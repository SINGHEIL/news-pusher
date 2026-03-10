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
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            response = requests.get(url, headers=headers, timeout=10)
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
    
    def send_single_message(self, content: str, touser: str) -> bool:
        """发送单条消息"""
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={self.access_token}"
        
        message = {
            "touser": touser,
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        json_data = json.dumps(message, ensure_ascii=False)
        response = requests.post(url, data=json_data.encode('utf-8'), headers=headers, timeout=10)
        result = response.json()
        
        logger.info(f"消息发送结果: {result}")
        return result.get('errcode') == 0
    
    def send_text_message(self, content: str) -> bool:
        """发送文本消息（支持分段发送）"""
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        try:
            if self.config.get('WECHAT_TEST'):
                touser = self.config.get('WECHAT_TEST_TOUSER')
                
                # 处理内容：去除多余空行，确保非空
                processed_content = content.strip()
                if not processed_content:
                    processed_content = "今日暂无新闻更新"
                
                # 微信API限制：2048字节，中文字符占3字节，每条最多约680字符
                max_chars_per_msg = 680
                
                # 如果内容超过限制，分段发送
                if len(processed_content) <= max_chars_per_msg:
                    logger.info(f"发送单条消息，长度: {len(processed_content)} 字符")
                    return self.send_single_message(processed_content, touser)
                else:
                    logger.info(f"内容过长，将分段发送，总长度: {len(processed_content)} 字符")
                    
                    # 按行分割，尽量在换行处分段
                    lines = processed_content.split('\n')
                    current_msg = ""
                    success_count = 0
                    msg_count = 0
                    
                    for line in lines:
                        # 如果加上这一行不会超限
                        if len(current_msg + '\n' + line) <= max_chars_per_msg:
                            if current_msg:
                                current_msg += '\n' + line
                            else:
                                current_msg = line
                        else:
                            # 发送当前消息
                            if current_msg:
                                msg_count += 1
                                logger.info(f"发送第 {msg_count} 段，长度: {len(current_msg)} 字符")
                                if self.send_single_message(current_msg, touser):
                                    success_count += 1
                                # 添加延迟避免发送过快
                                import time
                                time.sleep(0.5)
                            
                            # 开始新消息
                            current_msg = line
                    
                    # 发送最后一段
                    if current_msg:
                        msg_count += 1
                        logger.info(f"发送第 {msg_count} 段，长度: {len(current_msg)} 字符")
                        if self.send_single_message(current_msg, touser):
                            success_count += 1
                    
                    logger.info(f"分段发送完成: {success_count}/{msg_count} 成功")
                    return success_count == msg_count
            else:
                logger.info("正式号建议使用模板消息")
                return False
                
        except Exception as e:
            logger.error(f"发送微信消息异常: {str(e)}")
            return False
    
    def format_and_send(self, report: str) -> bool:
        """格式化并发送推送"""
        return self.send_text_message(report)
    
    def send_news_report(self, title: str, content: str) -> bool:
        """发送新闻报告"""
        if self.config.get('WECHAT_TEST'):
            full_content = f"{title}\n\n{content}"
            return self.send_text_message(full_content)
        else:
            data = {
                "first": {
                    "value": title,
                    "color": "#173177"
                },
                "content": {
                    "value": content[:500],
                    "color": "#173177"
                },
                "remark": {
                    "value": "\n点击查看详情",
                    "color": "#173177"
                }
            }
            return self.send_template_message(data)
