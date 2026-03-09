import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ExamNewsFetcher:
    """公考财会新闻抓取类"""
    
    def __init__(self):
        self.sources = {
            '公考': {
                '广东省人事考试网': 'http://rsks.gd.gov.cn',
                '珠海市人力资源和社会保障局': 'https://www.zhuhai.gov.cn/zhwsbs',
                '横琴粤澳深度合作区': 'https://www.hengqin.gov.cn',
            },
            '政策': {
                '财政部官网': 'http://www.mof.gov.cn',
                '中国会计报': 'http://www.cpanet.cn',
                '广东省财政厅': 'http://czt.gd.gov.cn',
            },
            '综合': {
                '人民日报': 'http://www.people.com.cn',
                '新华社': 'http://www.xinhuanet.com',
            }
        }
        
        # RSS源（如果有的话）
        self.rss_sources = {
            '公考': [],
            '政策': [],
            '综合': [
                'https://www.people.com.cn/rss/politics.xml',
                'https://www.xinhuanet.com/politics/news_politics.xml',
            ]
        }
    
    def fetch_webpage(self, url: str) -> str:
        """抓取网页内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            logger.error(f"抓取网页 {url} 失败: {str(e)}")
            return ''
    
    def parse_guangdong_exam(self) -> List[Dict]:
        """解析广东人事考试网"""
        news_list = []
        try:
            url = 'http://rsks.gd.gov.cn'
            html = self.fetch_webpage(url)
            if not html:
                return news_list
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找新闻标题（根据实际网页结构调整选择器）
            news_items = soup.find_all('div', class_='news-item') or soup.find_all('a', href=True)
            
            for item in news_items[:10]:
                if item.get('href') and not item.get('href').startswith('javascript'):
                    title = item.get_text(strip=True)
                    link = item.get('href')
                    if not link.startswith('http'):
                        link = url + link if link.startswith('/') else url + '/' + link
                    
                    news_list.append({
                        'title': title,
                        'link': link,
                        'category': '公考',
                        'source': '广东省人事考试网',
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
            
            logger.info(f"从广东省人事考试网抓取到 {len(news_list)} 条")
        except Exception as e:
            logger.error(f"解析广东人事考试网失败: {str(e)}")
        
        return news_list
    
    def parse_hengqin(self) -> List[Dict]:
        """解析横琴官网"""
        news_list = []
        try:
            url = 'https://www.hengqin.gov.cn'
            html = self.fetch_webpage(url)
            if not html:
                return news_list
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找政策、招聘等栏目
            keywords = ['财会', '招聘', '公告', '政策', '优惠', '金融']
            news_items = soup.find_all('a', href=True)
            
            for item in news_items:
                title = item.get_text(strip=True)
                if any(kw in title for kw in keywords):
                    link = item.get('href')
                    if not link.startswith('http'):
                        link = url + link if link.startswith('/') else url + '/' + link
                    
                    news_list.append({
                        'title': title,
                        'link': link,
                        'category': '政策',
                        'source': '横琴粤澳深度合作区',
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                    
                    if len(news_list) >= 5:
                        break
            
            logger.info(f"从横琴官网抓取到 {len(news_list)} 条")
        except Exception as e:
            logger.error(f"解析横琴官网失败: {str(e)}")
        
        return news_list
    
    def parse_ministry_finance(self) -> List[Dict]:
        """解析财政部官网"""
        news_list = []
        try:
            url = 'http://www.mof.gov.cn'
            html = self.fetch_webpage(url)
            if not html:
                return news_list
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找会计准则、政策更新等
            keywords = ['会计', '准则', '政策', '通知', '公告']
            news_items = soup.find_all('a', href=True)
            
            for item in news_items:
                title = item.get_text(strip=True)
                if any(kw in title for kw in keywords):
                    link = item.get('href')
                    if not link.startswith('http'):
                        link = url + link if link.startswith('/') else url + '/' + link
                    
                    news_list.append({
                        'title': title,
                        'link': link,
                        'category': '政策',
                        'source': '财政部官网',
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                    
                    if len(news_list) >= 5:
                        break
            
            logger.info(f"从财政部官网抓取到 {len(news_list)} 条")
        except Exception as e:
            logger.error(f"解析财政部官网失败: {str(e)}")
        
        return news_list
    
    def fetch_from_rss(self, url: str, category: str) -> List[Dict]:
        """从RSS源抓取"""
        try:
            feed = feedparser.parse(url)
            news_list = []
            
            for entry in feed.entries[:5]:
                news_list.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'category': category,
                    'source': feed.feed.get('title', url),
                    'date': entry.get('published', datetime.now().strftime('%Y-%m-%d'))
                })
            
            logger.info(f"从RSS {url} 抓取到 {len(news_list)} 条")
            return news_list
            
        except Exception as e:
            logger.error(f"抓取RSS {url} 失败: {str(e)}")
            return []
    
    def fetch_all_news(self) -> Dict[str, List[Dict]]:
        """抓取所有新闻源"""
        all_news = {
            '公考': [],
            '政策': [],
            '综合': []
        }
        
        # 抓取各个网站
        all_news['公考'].extend(self.parse_guangdong_exam())
        all_news['政策'].extend(self.parse_hengqin())
        all_news['政策'].extend(self.parse_ministry_finance())
        
        # 抓取RSS源
        for category, rss_urls in self.rss_sources.items():
            for rss_url in rss_urls:
                all_news[category].extend(self.fetch_from_rss(rss_url, category))
        
        return all_news
