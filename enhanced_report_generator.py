#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版简报生成器 - 生成带AI分析的文字简报
"""

import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedReportGenerator:
    """增强版简报生成器"""
    
    def __init__(self):
        pass
    
    def generate_news_report(self, all_news: Dict[str, List[Dict]]) -> str:
        """生成完整的文字简报（带AI分析）"""
        report_parts = []
        date = datetime.now().strftime('%Y年%m月%d日')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][datetime.now().weekday()]
        
        # 报表头
        report_parts.append(f"📊 {date} {weekday} 每日政经军简报")
        report_parts.append("=" * 45)
        report_parts.append("")
        
        # 统计总览
        total_news = sum(len(news) for news in all_news.values())
        report_parts.append(f"📈 今日资讯总数：{total_news}条")
        report_parts.append("🤖 AI智能分析已启用")
        report_parts.append("")
        
        # 政治新闻
        if all_news['政治']:
            report_parts.append("【政治要闻】")
            report_parts.append("-" * 25)
            for i, news in enumerate(all_news['政治'], 1):
                report_parts.append(f"\n{i}. {news['title']}")
                if news.get('summary'):
                    report_parts.append(f"   💡 {news['summary']}")
                if news.get('evaluation'):
                    report_parts.append(f"   📌 {news['evaluation']}")
                if news.get('suggestion'):
                    report_parts.append(f"   ✅ {news['suggestion']}")
            report_parts.append("")
        
        # 财经新闻（炒股支持）
        if all_news['财经']:
            report_parts.append("【财经聚焦】")
            report_parts.append("-" * 25)
            report_parts.append("💡 投资参考：市场动态与政策导向")
            report_parts.append("")
            for i, news in enumerate(all_news['财经'], 1):
                report_parts.append(f"\n{i}. {news['title']}")
                if news.get('summary'):
                    report_parts.append(f"   💡 {news['summary']}")
                if news.get('evaluation'):
                    report_parts.append(f"   📌 {news['evaluation']}")
                if news.get('suggestion'):
                    report_parts.append(f"   💰 {news['suggestion']}")
            report_parts.append("")
        
        # 军事新闻
        if all_news['军事']:
            report_parts.append("【军情速递】")
            report_parts.append("-" * 25)
            for i, news in enumerate(all_news['军事'], 1):
                report_parts.append(f"\n{i}. {news['title']}")
                if news.get('summary'):
                    report_parts.append(f"   💡 {news['summary']}")
                if news.get('evaluation'):
                    report_parts.append(f"   📌 {news['evaluation']}")
                if news.get('suggestion'):
                    report_parts.append(f"   ✅ {news['suggestion']}")
            report_parts.append("")
        
        # 公考新闻
        if all_news['公考']:
            report_parts.append("【公考资讯】")
            report_parts.append("-" * 25)
            for i, news in enumerate(all_news['公考'], 1):
                report_parts.append(f"\n{i}. {news['title']}")
                if news.get('summary'):
                    report_parts.append(f"   💡 {news['summary']}")
                if news.get('evaluation'):
                    report_parts.append(f"   📌 {news['evaluation']}")
                if news.get('suggestion'):
                    report_parts.append(f"   📝 {news['suggestion']}")
            report_parts.append("")
        
        # 政策动态
        if all_news['政策']:
            report_parts.append("【政策动态】")
            report_parts.append("-" * 25)
            for i, news in enumerate(all_news['政策'], 1):
                report_parts.append(f"\n{i}. {news['title']}")
                if news.get('summary'):
                    report_parts.append(f"   💡 {news['summary']}")
                if news.get('evaluation'):
                    report_parts.append(f"   📌 {news['evaluation']}")
                if news.get('suggestion'):
                    report_parts.append(f"   ✅ {news['suggestion']}")
            report_parts.append("")
        
        # 报表尾
        report_parts.append("=" * 45)
        report_parts.append("📮 本简报由AI自动生成，仅供参考")
        
        return "\n".join(report_parts)
    
    def filter_and_format(self, all_news: Dict[str, List[Dict]]) -> str:
        """筛选并格式化新闻"""
        return self.generate_news_report(all_news)
