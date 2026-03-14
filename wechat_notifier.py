import requests
import logging
import time
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class WeChatNotifier:
    """推送类 - 使用 Server酱推送到微信（无IP限制，免费）"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def send_serverchan(self, title: str, content: str) -> bool:
        """
        通过 Server酱 推送消息到微信
        文档: https://sct.ftqq.com
        """
        sendkey = self.config.get('SERVERCHAN_KEY', '')
        if not sendkey:
            logger.error("未配置 SERVERCHAN_KEY")
            return False
        
        url = f"https://sctapi.ftqq.com/{sendkey}.send"
        
        payload = {
            "title": title,
            "desp": content  # 支持 Markdown，无字数上限
        }
        
        try:
            response = requests.post(url, data=payload, timeout=15)
            result = response.json()
            logger.info(f"Server酱推送结果: {result}")
            
            code = result.get('code', -1)
            if code == 0:
                logger.info("✅ Server酱推送成功!")
                return True
            else:
                errmsg = result.get('message', '')
                logger.error(f"❌ Server酱推送失败! code={code}, message={errmsg}")
                return False
                
        except Exception as e:
            logger.error(f"Server酱推送异常: {str(e)}")
            return False

    def format_and_send(self, report: str) -> bool:
        """格式化并推送"""
        title = f"🌍 全球新闻速递 · {datetime.now().strftime('%Y年%m月%d日')}"
        
        # 将纯文本转为 Markdown 格式，Server酱支持完整 Markdown
        md_content = self._to_markdown(report)
        
        logger.info(f"准备推送，内容长度: {len(md_content)} 字符")
        return self.send_serverchan(title, md_content)

    def send_news_report(self, title: str, content: str) -> bool:
        """发送新闻报告"""
        md_content = self._to_markdown(content)
        return self.send_serverchan(title, md_content)

    def _to_markdown(self, text: str) -> str:
        """将纯文本转为 Markdown 格式"""
        lines = text.split('\n')
        md_lines = []
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                md_lines.append('')
            elif line_stripped.startswith('='):
                md_lines.append('---')
            elif line_stripped.startswith('-' * 5):
                md_lines.append('---')
            elif any(line_stripped.startswith(e) for e in ['🌍','🇨🇳','🌐','💰','📊','📅','📱','⏰']):
                md_lines.append(f"## {line_stripped}")
            elif line_stripped.startswith('【') and line_stripped.endswith('】'):
                md_lines.append(f"### {line_stripped}")
            else:
                md_lines.append(line_stripped)
        return '\n'.join(md_lines)
