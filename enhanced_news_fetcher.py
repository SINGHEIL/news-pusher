#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版新闻抓取器 - 支持政经军和财经新闻
提供正文内容抓取和AI智能总结
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from datetime import datetime
import re
import openai

logger = logging.getLogger(__name__)

class EnhancedNewsFetcher:
    """增强版新闻抓取器"""
    
    def __init__(self, api_key: str = ''):
        self.api_key = api_key
        # 政治新闻源
        self.political_sources = [
            {
                'name': '人民日报',
                'url': 'http://www.people.com.cn',
                'category': '政治',
                'list_selector': 'a[href*="/n1/"]',
                'content_selector': '.rm_txt_con'
            },
            {
                'name': '新华每日电讯',
                'url': 'http://www.xinhuanet.com',
                'category': '政治',
                'list_selector': 'a[href*="/politics/"]',
                'content_selector': '.main-aticle'
            }
        ]
        
        # 经济/财经新闻源（炒股支持）
        self.economic_sources = [
            {
                'name': '第一财经',
                'url': 'https://www.yicai.com',
                'category': '财经',
                'list_selector': 'a[href*="/news/"]',
                'content_selector': '.article-content'
            },
            {
                'name': '财新网',
                'url': 'https://www.caixin.com',
                'category': '财经',
                'list_selector': 'a[href*="/news/"]',
                'content_selector': '.article-content'
            },
            {
                'name': '新浪财经',
                'url': 'https://finance.sina.com.cn',
                'category': '财经',
                'list_selector': 'a[href*="/stock/"]',
                'content_selector': '.article'
            },
            {
                'name': '东方财富',
                'url': 'https://www.eastmoney.com',
                'category': '财经',
                'list_selector': 'a[href*="/news/"]',
                'content_selector': '.Body'
            }
        ]
        
        # 军事新闻源
        self.military_sources = [
            {
                'name': '环球网军事',
                'url': 'https://military.huanqiu.com',
                'category': '军事',
                'list_selector': 'a[href*="/article/"]',
                'content_selector': '.l-a-txt'
            }
        ]
        
        # 广东省本地新闻源（公考相关）
        self.local_sources = [
            {
                'name': '广东人社厅',
                'url': 'http://hrss.gd.gov.cn',
                'category': '公考',
                'list_selector': 'a[href*="/gwy/"]',
                'content_selector': '.content'
            },
            {
                'name': '横琴合作区',
                'url': 'https://www.hengqin.gov.cn',
                'category': '政策',
                'list_selector': 'a',
                'content_selector': '.article-content'
            }
        ]
    
    def fetch_webpage(self, url: str) -> str:
        """抓取网页内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            logger.error(f"抓取网页 {url} 失败: {str(e)}")
            return ''
    
    def extract_article_content(self, url: str, content_selector: str) -> str:
        """提取文章正文内容"""
        try:
            html = self.fetch_webpage(url)
            if not html:
                return ''
            
            soup = BeautifulSoup(html, 'html.parser')
            content_div = soup.select_one(content_selector)
            
            if content_div:
                # 移除广告和无关元素
                for element in content_div.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                    element.decompose()
                
                # 提取文本段落
                paragraphs = content_div.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                
                # 限制长度（最多1000字用于AI分析）
                if len(content) > 1000:
                    content = content[:1000]
                
                return content
            
            return ''
        except Exception as e:
            logger.error(f"提取文章内容失败 {url}: {str(e)}")
            return ''
    
    def ai_summarize_news(self, title: str, content: str, category: str) -> Dict:
        """使用AI总结新闻（支持DeepSeek免费API）"""
        if not self.api_key:
            return {
                'summary': content[:200] if content else '点击查看完整内容',
                'evaluation': '',
                'suggestion': ''
            }
        
        try:
            # 使用 DeepSeek API
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            prompt = f"""你是一名专业的新闻分析师，擅长分析{category}新闻。请对以下新闻进行分析：

标题：{title}
内容：{content}

请按以下格式输出（每项50字以内）：
【摘要】用一句话概括核心内容
【评价】客观评价这条新闻的重要性/影响
【建议】基于用户需求给出建议"""

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是专业的新闻分析师"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            
            # 解析AI输出
            summary = ''
            evaluation = ''
            suggestion = ''
            
            for line in result.split('\n'):
                if line.startswith('【摘要】'):
                    summary = line.replace('【摘要】', '').strip()
                elif line.startswith('【评价】'):
                    evaluation = line.replace('【评价】', '').strip()
                elif line.startswith('【建议】'):
                    suggestion = line.replace('【建议】', '').strip()
            
            return {
                'summary': summary if summary else (content[:200] if content else '点击查看完整内容'),
                'evaluation': evaluation,
                'suggestion': suggestion
            }
            
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            return {
                'summary': content[:200] if content else '点击查看完整内容',
                'evaluation': '',
                'suggestion': ''
            }
    
    def fetch_from_source(self, source: Dict, max_articles: int = 3) -> List[Dict]:
        """从指定源抓取新闻"""
        news_list = []
        try:
            html = self.fetch_webpage(source['url'])
            if not html:
                return news_list
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找新闻链接
            links = soup.select(source['list_selector'])
            
            for i, link in enumerate(links[:max_articles * 2]):
                if len(news_list) >= max_articles:
                    break
                
                title = link.get_text(strip=True)
                href = link.get('href', '')
                
                # 过滤无效链接
                if not title or len(title) < 10:
                    continue
                if not href or href.startswith('javascript'):
                    continue
                
                # 补全完整URL
                if not href.startswith('http'):
                    base_url = source['url']
                    href = base_url + href if href.startswith('/') else base_url + '/' + href
                
                # 提取正文内容
                content = self.extract_article_content(href, source.get('content_selector', ''))
                
                # AI分析
                ai_result = self.ai_summarize_news(title, content, source['category'])
                
                news_list.append({
                    'title': title,
                    'link': href,
                    'category': source['category'],
                    'source': source['name'],
                    'content': content,
                    'summary': ai_result['summary'],
                    'evaluation': ai_result['evaluation'],
                    'suggestion': ai_result['suggestion'],
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
                
                # 添加延迟
                import time
                time.sleep(1)
            
            logger.info(f"从 {source['name']} 抓取到 {len(news_list)} 条新闻")
        except Exception as e:
            logger.error(f"从 {source['name']} 抓取失败: {str(e)}")
        
        return news_list
    
    def fetch_all_news(self) -> Dict[str, List[Dict]]:
        """抓取所有新闻源"""
        all_news = {
            '政治': [],
            '财经': [],
            '军事': [],
            '公考': [],
            '政策': []
        }
        
        logger.info("开始抓取政治新闻...")
        for source in self.political_sources:
            all_news['政治'].extend(self.fetch_from_source(source, max_articles=2))
        
        logger.info("开始抓取财经新闻...")
        for source in self.economic_sources:
            all_news['财经'].extend(self.fetch_from_source(source, max_articles=2))
        
        logger.info("开始抓取军事新闻...")
        for source in self.military_sources:
            all_news['军事'].extend(self.fetch_from_source(source, max_articles=2))
        
        logger.info("开始抓取公考新闻...")
        for source in self.local_sources:
            category = source['category']
            if category in all_news:
                all_news[category].extend(self.fetch_from_source(source, max_articles=2))
        
        return all_news
