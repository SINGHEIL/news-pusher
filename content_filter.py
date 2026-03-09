import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentFilter:
    """内容筛选和摘要生成类"""
    
    def __init__(self, use_ai: bool = False, api_key: str = ''):
        self.use_ai = use_ai
        self.api_key = api_key
        
        # 关键词匹配规则
        self.keywords = {
            '公考': [
                '财会岗', '税务局', '财政局', '招聘', '考试', '公告', 
                '公务员', '事业单位', '招录', '报考', '资格'
            ],
            '政策': [
                '优惠政策', '横琴', '金融', '开放', '改革', '新区', 
                '会计法', '准则', '更新', '通知', '实施', '新质生产力',
                '大湾区', '产业', '投资', '补贴', '扶持'
            ],
            '专业课': [
                '会计', '审计', '财务', '税收', '预算', '决算',
                '准则', '制度', '规范', '标准', '处理', '核算'
            ]
        }
    
    def filter_news(self, all_news: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """筛选相关新闻"""
        filtered_news = {
            '公考': [],
            '政策': [],
            '综合': []
        }
        
        for category, news_list in all_news.items():
            for news in news_list:
                if self._is_relevant(news, category):
                    filtered_news[category].append(news)
        
        logger.info(f"筛选后: 公考{len(filtered_news['公考'])}条, "
                   f"政策{len(filtered_news['政策'])}条, "
                   f"综合{len(filtered_news['综合'])}条")
        
        return filtered_news
    
    def _is_relevant(self, news: Dict, category: str) -> bool:
        """判断新闻是否相关"""
        title = news.get('title', '').lower()
        
        # 检查该分类的关键词
        for kw in self.keywords[category]:
            if kw in title:
                return True
        
        # 特殊逻辑：横琴相关内容放在政策类
        if '横琴' in title and category == '综合':
            return True
        
        # 特殊逻辑：会计相关内容
        if any(kw in title for kw in self.keywords['专业课']):
            return True
        
        return False
    
    def generate_summary(self, news: Dict) -> str:
        """生成新闻摘要"""
        title = news.get('title', '')
        source = news.get('source', '')
        
        if self.use_ai and self.api_key:
            # 使用AI生成智能摘要
            return self._ai_summary(news)
        else:
            # 使用规则生成摘要
            return self._rule_summary(title, source, news.get('category', ''))
    
    def _rule_summary(self, title: str, source: str, category: str) -> str:
        """基于规则生成摘要"""
        summary = f"{title}\n来源: {source}"
        
        # 根据分类添加备考关联
        if category == '公考':
            summary += "\n关联: 可作为面试素材"
        elif category == '政策':
            summary += "\n关联: 关注政策变化"
        
        return summary
    
    def _ai_summary(self, news: Dict) -> str:
        """使用AI生成智能摘要"""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.openai.com/v1"
            )
            
            prompt = f"""
你是一名专业的财会公考导师。请为以下新闻生成一个精炼摘要，要求：
1. 核心事实（30字以内）
2. 备考/职业关联度（50字以内）

新闻标题: {news['title']}
新闻来源: {news['source']}
分类: {news['category']}

请用以下格式输出：
核心事实：XXX
备考关联：XXX
"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是专业的财会公考导师"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI摘要生成失败: {str(e)}")
            return self._rule_summary(news['title'], news['source'], news['category'])
    
    def format_report(self, filtered_news: Dict[str, List[Dict]]) -> str:
        """格式化为Markdown简报（精简版）"""
        report = []
        date = datetime.now().strftime('%Y年%m月%d日')
        
        report.append(f"📅 每日财会备考简报 - {date}\n")
        
        # 公考热点
        if filtered_news['公考']:
            report.append("【公考热点】")
            for i, news in enumerate(filtered_news['公考'][:2], 1):
                report.append(f"{i}. {news['title'][:30]}...")
                report.append(f"   {news['source']}")
            report.append("")
        
        # 政策速递
        if filtered_news['政策']:
            report.append("【政策速递】")
            for i, news in enumerate(filtered_news['政策'][:2], 1):
                report.append(f"{i}. {news['title'][:30]}...")
                report.append(f"   {news['source']}")
            report.append("")
        
        # 专业课更新
        if filtered_news['综合']:
            report.append("【专业课更新】")
            for i, news in enumerate(filtered_news['综合'][:2], 1):
                report.append(f"\n{i}. {news['title']}")
                report.append(f"   来源: {news['source']}")
                summary = self.generate_summary(news)
                report.append(f"   {summary}")
                report.append(f"   链接: {news['link']}")
            report.append("")
        
        # 只显示总数
        report.append(f"\n共 {sum(len(news) for news in filtered_news.values())} 条新闻")
        
        return "\n".join(report)
