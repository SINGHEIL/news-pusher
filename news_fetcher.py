import requests
from bs4 import BeautifulSoup
import feedparser
import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsFetcher:
    """新闻抓取类"""
    
    def __init__(self):
        self.sources = {
            '政治': [
                'https://feeds.bbci.co.uk/chinese/simp/news/rss.xml',
                'https://cn.reuters.com/rssFeed/CNTopGenNews',
            ],
            '经济': [
                'https://cn.reuters.com/rssFeed/CNBusinessNews',
                'https://www.ftchinese.com/rss/feed',
            ],
            '军事': [
                'https://feeds.bbci.co.uk/chinese/simp/world/rss.xml',
                'https://www.reuters.com/rssFeed/worldNews',
            ]
        }
    
    def fetch_from_rss(self, url: str, category: str) -> List[Dict]:
        """从RSS源抓取新闻"""
        try:
            feed = feedparser.parse(url)
            news_list = []
            
            for entry in feed.entries[:10]:  # 每个源取前10条
                news_item = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    'category': category,
                    'source': feed.feed.get('title', url)
                }
                news_list.append(news_item)
            
            logger.info(f"从 {url} 抓取到 {len(news_list)} 条 {category} 新闻")
            return news_list
            
        except Exception as e:
            logger.error(f"抓取RSS {url} 失败: {str(e)}")
            return []
    
    def fetch_all_news(self, categories: List[str]) -> Dict[str, List[Dict]]:
        """抓取所有指定分类的新闻"""
        all_news = {}
        
        for category in categories:
            if category in self.sources:
                category_news = []
                for rss_url in self.sources[category]:
                    news_items = self.fetch_from_rss(rss_url, category)
                    category_news.extend(news_items)
                all_news[category] = category_news
                logger.info(f"{category} 类别共抓取 {len(category_news)} 条新闻")
        
        return all_news
    
    def format_news(self, all_news: Dict[str, List[Dict]]) -> str:
        """格式化新闻为文本"""
        formatted_text = []
        formatted_text.append("=" * 50)
        formatted_text.append(f"新闻推送 - {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
        formatted_text.append("=" * 50)
        formatted_text.append("")
        
        for category, news_list in all_news.items():
            if news_list:
                formatted_text.append(f"\n【{category}】")
                formatted_text.append("-" * 30)
                for i, news in enumerate(news_list[:5], 1):  # 每个类别最多显示5条
                    formatted_text.append(f"\n{i}. {news['title']}")
                    formatted_text.append(f"   来源: {news['source']}")
                    formatted_text.append(f"   时间: {news['published']}")
                    formatted_text.append(f"   链接: {news['link']}")
                    if news['summary']:
                        formatted_text.append(f"   摘要: {news['summary'][:100]}...")
                formatted_text.append("")
        
        formatted_text.append("=" * 50)
        formatted_text.append(f"共抓取 {sum(len(news) for news in all_news.values())} 条新闻")
        formatted_text.append("=" * 50)
        
        return "\n".join(formatted_text)
