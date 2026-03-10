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
                '公务员', '事业单位', '招录', '报考', '资格', '报名',
                '面试', '体检', '公示', '录用'
            ],
            '政策': [
                '优惠政策', '横琴', '金融', '开放', '改革', '新区', 
                '会计法', '准则', '更新', '通知', '实施', '新质生产力',
                '大湾区', '产业', '投资', '补贴', '扶持', '退税',
                '减税', '免税', '税率'
            ],
            '专业课': [
                '会计', '审计', '财务', '税收', '预算', '决算',
                '准则', '制度', '规范', '标准', '处理', '核算',
                '资产', '负债', '收入', '费用', '利润'
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
    
    def extract_key_info(self, title: str) -> str:
        """从标题提取关键信息"""
        key_info = []
        
        # 提取日期
        import re
        date_pattern = r'\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}月\d{1,2}日'
        dates = re.findall(date_pattern, title)
        if dates:
            key_info.append(f"📅 {dates[0]}")
        
        # 提取数字（如招聘人数、金额等）
        numbers = re.findall(r'\d+(?:,\d{3})*(?:万|亿|人|元|个|项)?', title)
        if numbers:
            key_info.append(f"🔢 {', '.join(numbers[:3])}")
        
        return ' '.join(key_info)
    
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
        summary = []
        
        # 提取关键信息
        key_info = self.extract_key_info(title)
        if key_info:
            summary.append(key_info)
        
        # 根据分类添加备考关联
        if category == '公考':
            summary.append("💼 可作为面试素材")
        elif category == '政策':
            summary.append("📌 关注政策变化")
        elif category == '综合':
            summary.append("📖 财会相关知识")
        
        return ' '.join(summary) if summary else "👇 查看详情"
    
    def format_report(self, filtered_news: Dict[str, List[Dict]]) -> str:
        """格式化为Markdown简报（优化版）"""
        report = []
        date = datetime.now().strftime('%Y年%m月%d日')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][datetime.now().weekday()]
        
        report.append(f"📅 每日财会备考简报 - {date} {weekday}")
        report.append(f"{'='*35}\n")
        
        # 公考热点
        if filtered_news['公考']:
            report.append("【公考热点】")
            for i, news in enumerate(filtered_news['公考'][:3], 1):
                report.append(f"\n{i}. {news['title']}")
                report.append(f"   📍 {news['source']}")
                key_info = self.extract_key_info(news['title'])
                if key_info:
                    report.append(f"   {key_info}")
                report.append(f"   💼 面试素材/报考参考")
                if news.get('link'):
                    report.append(f"   🔗 {news['link']}")
            report.append("")
        
        # 政策速递
        if filtered_news['政策']:
            report.append("【政策速递】")
            for i, news in enumerate(filtered_news['政策'][:3], 1):
                report.append(f"\n{i}. {news['title']}")
                report.append(f"   📍 {news['source']}")
                key_info = self.extract_key_info(news['title'])
                if key_info:
                    report.append(f"   {key_info}")
                report.append(f"   📌 关注政策动向")
                if news.get('link'):
                    report.append(f"   🔗 {news['link']}")
            report.append("")
        
        # 专业课更新
        if filtered_news['综合']:
            report.append("【财会相关】")
            for i, news in enumerate(filtered_news['综合'][:2], 1):
                report.append(f"\n{i}. {news['title']}")
                report.append(f"   📍 {news['source']}")
                report.append(f"   📖 财会知识点")
                if news.get('link'):
                    report.append(f"   🔗 {news['link']}")
            report.append("")
        
        # 统计信息
        total = sum(len(news) for news in filtered_news.values())
        report.append(f"\n{'='*35}")
        report.append(f"📊 今日共收录 {total} 条资讯")
        report.append(f"💡 提示：点击链接查看完整内容")
        
        return "\n".join(report)
