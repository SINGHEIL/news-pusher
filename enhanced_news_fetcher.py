#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版新闻抓取器 - 支持政经军和财经新闻
提供高质量、时效性强、去重的新闻抓取
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import re
import openai
import hashlib

logger = logging.getLogger(__name__)

class EnhancedNewsFetcher:
    """增强版新闻抓取器"""
    
    def __init__(self, api_key: str = ''):
        self.api_key = api_key
        self.seen_news = set()  # 去重集合
        self.max_articles_per_category = 10  # 每个分类最多抓取10条
        
        # 高质量政治新闻源（时效性强）
        self.political_sources = [
            {
                'name': '央视新闻',
                'url': 'https://news.cctv.com',
                'category': '政治',
                'list_selector': 'a[href*="/news/"], a[href*="/politics/"]',
                'content_selector': '.content',
                'fetch_method': 'http'
            },
            {
                'name': '新华社',
                'url': 'https://www.news.cn',
                'category': '政治',
                'list_selector': 'a[href*="/politics/"], a[href*="/china/"]',
                'content_selector': '.main-aticle',
                'fetch_method': 'http'
            },
            {
                'name': '人民网时政',
                'url': 'http://politics.people.com.cn',
                'category': '政治',
                'list_selector': 'a[href*="/n1/"]',
                'content_selector': '.rm_txt_con',
                'fetch_method': 'http'
            },
            {
                'name': '环球网时政',
                'url': 'https://china.huanqiu.com',
                'category': '政治',
                'list_selector': 'a[href*="/article/"]',
                'content_selector': '.l-a-txt',
                'fetch_method': 'http'
            },
            {
                'name': '澎湃新闻时政',
                'url': 'https://www.thepaper.cn',
                'category': '政治',
                'list_selector': 'a[href*="/newsDetail_forward_"]',
                'content_selector': '.news_txt',
                'fetch_method': 'http'
            }
        ]
        
        # 高质量财经新闻源（炒股支持）
        self.economic_sources = [
            {
                'name': '华尔街见闻',
                'url': 'https://wallstreetcn.com',
                'category': '财经',
                'list_selector': 'a[href*="/articles/"]',
                'content_selector': '.article-content',
                'fetch_method': 'http'
            },
            {
                'name': '雪球热榜',
                'url': 'https://xueqiu.com',
                'category': '财经',
                'list_selector': 'a[href*="/stock/"], a[href*="/S/"]',
                'content_selector': '.article-content',
                'fetch_method': 'http'
            },
            {
                'name': '同花顺快讯',
                'url': 'https://news.10jqka.com.cn',
                'category': '财经',
                'list_selector': 'a[href*="/article/"]',
                'content_selector': '.article-content',
                'fetch_method': 'http'
            },
            {
                'name': '财联社电报',
                'url': 'https://www.cls.cn',
                'category': '财经',
                'list_selector': 'a[href*="/telegraph/"]',
                'content_selector': '.detail-content',
                'fetch_method': 'http'
            },
            {
                'name': '经济参考报',
                'url': 'http://www.jjckb.cn',
                'category': '财经',
                'list_selector': 'a[href*="/content_"]',
                'content_selector': '.content',
                'fetch_method': 'http'
            },
            {
                'name': '东方财富快讯',
                'url': 'https://kuaixun.eastmoney.com',
                'category': '财经',
                'list_selector': 'a[href*="/detail/"]',
                'content_selector': '.body',
                'fetch_method': 'http'
            }
        ]
        
        # 高质量军事新闻源
        self.military_sources = [
            {
                'name': '解放军报',
                'url': 'http://www.81.cn',
                'category': '军事',
                'list_selector': 'a[href*="/jfjbmap/"]',
                'content_selector': '.content',
                'fetch_method': 'http'
            },
            {
                'name': '中国军网',
                'url': 'http://www.81.cn',
                'category': '军事',
                'list_selector': 'a[href*="/content/"]',
                'content_selector': '.article-content',
                'fetch_method': 'http'
            },
            {
                'name': '参考消息军事',
                'url': 'https://www.cankaoxiaoxi.com/mil',
                'category': '军事',
                'list_selector': 'a[href*="/mil/"]',
                'content_selector': '.article-content',
                'fetch_method': 'http'
            },
            {
                'name': '凤凰网军事',
                'url': 'https://mil.ifeng.com',
                'category': '军事',
                'list_selector': 'a[href*="/c/"]',
                'content_selector': '.article-content',
                'fetch_method': 'http'
            }
        ]
        
        # 公考/政策新闻源
        self.local_sources = [
            {
                'name': '国家公务员局',
                'url': 'http://www.scs.gov.cn',
                'category': '公考',
                'list_selector': 'a[href*="/gwy/"], a[href*="/gkzp/"]',
                'content_selector': '.content',
                'fetch_method': 'http'
            },
            {
                'name': '广东省人社厅',
                'url': 'http://hrss.gd.gov.cn',
                'category': '公考',
                'list_selector': 'a[href*="/gwy/"], a[href*="/zwgk/"]',
                'content_selector': '.content',
                'fetch_method': 'http'
            },
            {
                'name': '横琴合作区',
                'url': 'https://www.hengqin.gov.cn',
                'category': '政策',
                'list_selector': 'a[href*="/content/"]',
                'content_selector': '.article-content',
                'fetch_method': 'http'
            }
        ]
    
    def generate_fingerprint(self, title: str, content: str) -> str:
        """生成新闻指纹用于去重"""
        # 使用标题和内容前100字符生成指纹
        text = title + content[:100] if content else title
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def fetch_webpage(self, url: str) -> str:
        """抓取网页内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # 增加超时时间，添加重试机制
            for attempt in range(3):
                try:
                    response = requests.get(url, headers=headers, timeout=20)
                    response.encoding = 'utf-8'
                    
                    if response.status_code == 200:
                        return response.text
                    else:
                        logger.warning(f"抓取 {url} 失败，状态码: {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"抓取 {url} 超时，第 {attempt+1} 次重试")
                    continue
                
                except Exception as e:
                    logger.warning(f"抓取 {url} 异常: {str(e)}，第 {attempt+1} 次重试")
                    continue
            
            return ''
            
        except Exception as e:
            logger.error(f"抓取网页 {url} 失败: {str(e)}")
            return ''
    
    def extract_article_content(self, url: str, content_selector: str) -> str:
        """提取文章正文内容（优化版）"""
        try:
            html = self.fetch_webpage(url)
            if not html:
                return ''
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 先尝试使用选择器
            if content_selector:
                content_div = soup.select_one(content_selector)
                if content_div:
                    # 移除广告和无关元素
                    for element in content_div.find_all(['script', 'style', 'nav', 'footer', 'aside', 'div[class*="ad"]']):
                        element.decompose()
                    
                    # 提取文本段落
                    paragraphs = content_div.find_all('p')
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    
                    if content and len(content) > 50:
                        # 限制长度（最多800字用于AI分析）
                        if len(content) > 800:
                            content = content[:800]
                        return content
            
            # 如果选择器失效，尝试通用方法
            # 查找所有正文段落
            paragraphs = soup.find_all('p')
            content_parts = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                # 过滤广告、版权等短文本
                if len(text) > 20 and not any(keyword in text for keyword in ['广告', '版权', 'Copyright', '©']):
                    content_parts.append(text)
            
            content = '\n'.join(content_parts)
            
            if content:
                # 限制长度（最多800字用于AI分析）
                if len(content) > 800:
                    content = content[:800]
                return content
            else:
                return ''
                
        except Exception as e:
            logger.error(f"提取文章内容失败 {url}: {str(e)}")
            return ''
    
    def filter_by_time(self, title: str, content: str) -> bool:
        """根据时间过滤新闻（确保时效性）"""
        # 检查标题中是否包含今天或昨天的日期
        today = datetime.now().strftime('%m月%d日')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%m月%d日')
        
        date_patterns = [
            today,
            yesterday,
            datetime.now().strftime('%Y年%m月%d日'),
            (datetime.now() - timedelta(days=1)).strftime('%Y年%m月%d日'),
            '今天',
            '昨日'
        ]
        
        # 如果包含日期关键词，优先保留
        for pattern in date_patterns:
            if pattern in title:
                return True
        
        # 检查是否包含"最新"、"快讯"等时效性词汇
        time_keywords = ['最新', '快讯', '刚刚', '今日', '突发']
        for keyword in time_keywords:
            if keyword in title:
                return True
        
        # 默认保留，但长度太短的新闻可能质量不高
        if len(title) < 15:
            return False
            
        return True
    
    def ai_summarize_news(self, title: str, content: str, category: str) -> Dict:
        """使用AI总结新闻（支持DeepSeek免费API）"""
        if not self.api_key:
            return {
                'summary': content[:150] if content else '点击查看完整内容',
                'evaluation': '',
                'suggestion': ''
            }
        
        try:
            # 使用 DeepSeek API
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            # 根据分类调整提示词
            category_prompts = {
                '政治': '你是一名政治分析师',
                '财经': '你是一名财经分析师，特别关注股市投资机会',
                '军事': '你是一名军事分析专家',
                '公考': '你是一名公务员考试辅导专家',
                '政策': '你是一名政策分析师'
            }
            
            role = category_prompts.get(category, '你是专业的新闻分析师')
            
            prompt = f"""{role}。请对以下新闻进行分析：

标题：{title}
内容：{content[:500]}

请按以下格式输出（每项50字以内）：
【摘要】用一句话概括核心内容
【评价】客观评价这条新闻的重要性/影响
【建议】基于用户需求给出建议"""

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": role},
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
                'summary': summary if summary else (content[:150] if content else '点击查看完整内容'),
                'evaluation': evaluation,
                'suggestion': suggestion
            }
            
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            return {
                'summary': content[:150] if content else '点击查看完整内容',
                'evaluation': '',
                'suggestion': ''
            }
    
    def fetch_from_source(self, source: Dict) -> List[Dict]:
        """从指定源抓取新闻（优化版）"""
        news_list = []
        try:
            html = self.fetch_webpage(source['url'])
            if not html:
                return news_list
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找新闻链接
            links = soup.select(source['list_selector'])
            
            for i, link in enumerate(links):
                if len(news_list) >= 5:  # 每个源最多抓取5条
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
                    if href.startswith('/'):
                        href = base_url + href
                    else:
                        href = base_url + '/' + href
                
                # 提取正文内容
                content = self.extract_article_content(href, source.get('content_selector', ''))
                
                # 生成指纹用于去重
                fingerprint = self.generate_fingerprint(title, content)
                if fingerprint in self.seen_news:
                    continue  # 跳过重复新闻
                
                # 时效性过滤
                if not self.filter_by_time(title, content):
                    continue
                
                # 添加去重指纹
                self.seen_news.add(fingerprint)
                
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
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'timestamp': datetime.now().timestamp()
                })
                
                # 添加延迟避免请求过快
                import time
                time.sleep(0.5)
            
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
            all_news['政治'].extend(self.fetch_from_source(source))
        
        logger.info("开始抓取财经新闻...")
        for source in self.economic_sources:
            all_news['财经'].extend(self.fetch_from_source(source))
        
        logger.info("开始抓取军事新闻...")
        for source in self.military_sources:
            all_news['军事'].extend(self.fetch_from_source(source))
        
        logger.info("开始抓取公考新闻...")
        for source in self.local_sources:
            category = source['category']
            if category in all_news:
                all_news[category].extend(self.fetch_from_source(source))
        
        # 按时间排序（最新的在前）
        for category in all_news:
            all_news[category].sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            # 每个分类最多保留10条
            all_news[category] = all_news[category][:self.max_articles_per_category]
        
        # 统计总数
        total = sum(len(news) for news in all_news.values())
        logger.info(f"抓取完成，总计 {total} 条新闻")
        
        return all_news
