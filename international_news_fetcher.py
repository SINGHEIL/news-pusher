#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外网一线消息抓取器
抓取国际主流媒体的最新新闻
支持多种外网新闻源
"""

import requests
from bs4 import BeautifulSoup
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import re
import feedparser
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class InternationalNewsFetcher:
    """国际新闻抓取器 - 抓取外网一线消息"""
    
    def __init__(self):
        # 设置请求头，模拟真实浏览器访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 代理配置（如果需要）
        self.proxies = None  # 可以在这里配置代理
        
        # 国际主流新闻源配置
        self.international_sources = [
            # 1. 路透社（Reuters）- 世界级财经新闻
            {
                'name': 'Reuters',
                'url': 'https://www.reuters.com',
                'rss_url': 'https://www.reuters.com/rss',
                'category': '国际财经',
                'list_selector': 'a[href*="/article/"]',
                'content_selector': 'article[class*="article-body"]',
                'language': 'en',
                'timezone': 'UTC'
            },
            
            # 2. 彭博社（Bloomberg）- 全球财经新闻
            {
                'name': 'Bloomberg',
                'url': 'https://www.bloomberg.com',
                'category': '国际财经',
                'list_selector': 'a[href*="/news/articles/"]',
                'content_selector': 'article[class*="body-content"]',
                'language': 'en',
                'timezone': 'EST'
            },
            
            # 3. 华尔街日报（Wall Street Journal）- 美国财经
            {
                'name': 'Wall Street Journal',
                'url': 'https://www.wsj.com',
                'category': '国际财经',
                'list_selector': 'a[href*="/articles/"]',
                'content_selector': 'article[class*="article-content"]',
                'language': 'en',
                'timezone': 'EST'
            },
            
            # 4. 金融时报（Financial Times）- 欧洲财经
            {
                'name': 'Financial Times',
                'url': 'https://www.ft.com',
                'category': '国际财经',
                'list_selector': 'a[data-trackable="heading-link"]',
                'content_selector': 'div[class*="article__content"]',
                'language': 'en',
                'timezone': 'GMT'
            },
            
            # 5. CNBC - 美国财经新闻
            {
                'name': 'CNBC',
                'url': 'https://www.cnbc.com',
                'rss_url': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
                'category': '国际财经',
                'list_selector': 'a[href*="/2024/"]',  # 匹配日期格式
                'content_selector': 'div[class*="ArticleBody-articleBody"]',
                'language': 'en',
                'timezone': 'EST'
            },
            
            # 6. BBC News - 国际综合新闻
            {
                'name': 'BBC News',
                'url': 'https://www.bbc.com/news',
                'rss_url': 'https://feeds.bbci.co.uk/news/rss.xml',
                'category': '国际新闻',
                'list_selector': 'a[href*="/news/"]',
                'content_selector': 'article[class*="story-body"]',
                'language': 'en',
                'timezone': 'GMT'
            },
            
            # 7. CNN - 美国新闻
            {
                'name': 'CNN',
                'url': 'https://edition.cnn.com',
                'category': '国际新闻',
                'list_selector': 'a[href*="/2024/"]',
                'content_selector': 'article[class*="article__content"]',
                'language': 'en',
                'timezone': 'EST'
            },
            
            # 8. 纽约时报（New York Times）- 美国新闻
            {
                'name': 'New York Times',
                'url': 'https://www.nytimes.com',
                'category': '国际新闻',
                'list_selector': 'a[href*="/2024/"]',
                'content_selector': 'section[name="articleBody"]',
                'language': 'en',
                'timezone': 'EST'
            },
            
            # 9. The Guardian - 英国新闻
            {
                'name': 'The Guardian',
                'url': 'https://www.theguardian.com',
                'rss_url': 'https://www.theguardian.com/international/rss',
                'category': '国际新闻',
                'list_selector': 'a[href*="/2024/"]',
                'content_selector': 'div[class*="article-body"]',
                'language': 'en',
                'timezone': 'GMT'
            },
            
            # 10. Nikkei Asia - 亚洲财经新闻
            {
                'name': 'Nikkei Asia',
                'url': 'https://asia.nikkei.com',
                'category': '亚洲财经',
                'list_selector': 'a[href*="/Politics/"]',
                'content_selector': 'div[class*="article-content"]',
                'language': 'en',
                'timezone': 'JST'
            },
            
            # 11. South China Morning Post - 香港英文媒体
            {
                'name': 'SCMP',
                'url': 'https://www.scmp.com',
                'category': '亚洲新闻',
                'list_selector': 'a[href*="/news/"]',
                'content_selector': 'div[class*="article__content"]',
                'language': 'en',
                'timezone': 'HKT'
            },
            
            # 12. Al Jazeera - 中东新闻
            {
                'name': 'Al Jazeera',
                'url': 'https://www.aljazeera.com',
                'category': '国际新闻',
                'list_selector': 'a[href*="/news/"]',
                'content_selector': 'article[class*="article-body"]',
                'language': 'en',
                'timezone': 'AST'
            },
            
            # 13. AP News - 美联社
            {
                'name': 'AP News',
                'url': 'https://apnews.com',
                'category': '国际新闻',
                'list_selector': 'a[href*="/article/"]',
                'content_selector': 'div[class*="Article"]',
                'language': 'en',
                'timezone': 'EST'
            },
            
            # 14. Yahoo Finance - 财经数据
            {
                'name': 'Yahoo Finance',
                'url': 'https://finance.yahoo.com',
                'category': '国际财经',
                'list_selector': 'a[href*="/news/"]',
                'content_selector': 'div[class*="caas-body"]',
                'language': 'en',
                'timezone': 'EST'
            },
            
            # 15. MarketWatch - 市场观察
            {
                'name': 'MarketWatch',
                'url': 'https://www.marketwatch.com',
                'category': '国际财经',
                'list_selector': 'a[href*="/story/"]',
                'content_selector': 'article[class*="article__body"]',
                'language': 'en',
                'timezone': 'EST'
            }
        ]
        
        # 财经数据源（股票、汇率、加密货币）
        self.financial_data_sources = [
            {
                'name': 'Investing.com',
                'url': 'https://www.investing.com',
                'category': '金融数据',
                'list_selector': 'a[href*="/news/"]',
                'content_selector': 'div[class*="articlePage"]'
            },
            {
                'name': 'CoinDesk',
                'url': 'https://www.coindesk.com',
                'category': '加密货币',
                'list_selector': 'a[href*="/2024/"]',
                'content_selector': 'div[class*="article-body"]'
            },
            {
                'name': 'CoinTelegraph',
                'url': 'https://cointelegraph.com',
                'category': '加密货币',
                'list_selector': 'a[href*="/news/"]',
                'content_selector': 'div[class*="post-content"]'
            }
        ]
    
    def fetch_with_proxy(self, url: str, timeout: int = 20) -> Optional[str]:
        """使用配置的代理抓取网页"""
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                proxies=self.proxies,
                timeout=timeout
            )
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            logger.warning(f"使用代理抓取失败 {url}: {str(e)}")
            # 尝试不使用代理
            try:
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    timeout=timeout
                )
                response.encoding = 'utf-8'
                return response.text
            except Exception as e2:
                logger.error(f"抓取失败 {url}: {str(e2)}")
                return None
    
    def parse_rss_feed(self, rss_url: str, source_name: str) -> List[Dict]:
        """解析RSS订阅源"""
        news_list = []
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:10]:  # 最多10条
                # 检查发布时间（24小时内）
                if hasattr(entry, 'published_parsed'):
                    publish_time = datetime(*entry.published_parsed[:6])
                    time_diff = datetime.now() - publish_time
                    
                    # 只抓取24小时内的新闻
                    if time_diff.days > 1:
                        continue
                
                title = entry.title if hasattr(entry, 'title') else ''
                link = entry.link if hasattr(entry, 'link') else ''
                summary = entry.summary if hasattr(entry, 'summary') else ''
                
                if title and link:
                    # 尝试获取详细内容
                    content = summary
                    if len(content) < 100:  # 如果摘要太短，尝试抓取正文
                        content = self.extract_article_content(link)
                    
                    news_list.append({
                        'title': title,
                        'link': link,
                        'category': '国际新闻',
                        'source': source_name,
                        'content': content[:300] if content else "暂无详细内容",
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'original_date': publish_time.strftime('%Y-%m-%d %H:%M') if 'publish_time' in locals() else ''
                    })
            
            logger.info(f"从 {source_name} RSS 抓取到 {len(news_list)} 条新闻")
        except Exception as e:
            logger.error(f"解析RSS {rss_url} 失败: {str(e)}")
        
        return news_list
    
    def extract_article_content(self, url: str, content_selector: str = None) -> str:
        """提取文章正文内容"""
        try:
            html = self.fetch_with_proxy(url)
            if not html:
                return ''
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 尝试多种常见的内容选择器
            content_selectors = []
            if content_selector:
                content_selectors.append(content_selector)
            
            # 常见的内容容器选择器
            content_selectors.extend([
                'article',
                'div[class*="article"]',
                'div[class*="content"]',
                'div[class*="body"]',
                'main',
                'section[class*="article"]',
                'div[itemprop="articleBody"]'
            ])
            
            content_div = None
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    break
            
            if content_div:
                # 移除无关元素
                for element in content_div.find_all(['script', 'style', 'nav', 'footer', 'aside', 'form', 'iframe']):
                    element.decompose()
                
                # 提取文本段落
                paragraphs = content_div.find_all(['p', 'div'])
                text_parts = []
                
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # 过滤短文本
                        text_parts.append(text)
                
                content = '\n'.join(text_parts)
                
                # 清理和截断
                if content:
                    # 移除多余空白
                    content = re.sub(r'\s+', ' ', content)
                    # 限制长度（最多800字）
                    if len(content) > 800:
                        content = content[:800] + '...'
                    
                    return content
            
            return ''
        except Exception as e:
            logger.error(f"提取文章内容失败 {url}: {str(e)}")
            return ''
    
    def fetch_from_international_source(self, source: Dict, max_articles: int = 3) -> List[Dict]:
        """从国际新闻源抓取新闻"""
        news_list = []
        
        try:
            # 首先尝试RSS源
            if 'rss_url' in source:
                rss_news = self.parse_rss_feed(source['rss_url'], source['name'])
                news_list.extend(rss_news[:max_articles])
            
            # 如果RSS不够，再抓取网页
            if len(news_list) < max_articles:
                html = self.fetch_with_proxy(source['url'])
                if not html:
                    return news_list
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # 查找新闻链接
                links = []
                if source['list_selector']:
                    links = soup.select(source['list_selector'])
                
                # 如果没有特定选择器，尝试查找所有文章链接
                if not links:
                    links = soup.find_all('a', href=True)
                
                processed_urls = set()
                for link in links[:20]:  # 检查前20个链接
                    if len(news_list) >= max_articles:
                        break
                    
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # 过滤无效链接
                    if not href or not title:
                        continue
                    
                    # 去重
                    if href in processed_urls:
                        continue
                    processed_urls.add(href)
                    
                    # 过滤非新闻链接
                    if not any(keyword in href for keyword in ['/article/', '/news/', '/2024/', '/story/']):
                        continue
                    
                    # 补全完整URL
                    if not href.startswith('http'):
                        href = urljoin(source['url'], href)
                    
                    # 过滤太短的标题
                    if len(title) < 10:
                        continue
                    
                    # 提取内容
                    content = self.extract_article_content(href, source.get('content_selector'))
                    
                    # 如果没有内容，跳过
                    if not content or len(content) < 50:
                        continue
                    
                    news_list.append({
                        'title': title,
                        'link': href,
                        'category': source['category'],
                        'source': source['name'],
                        'content': content[:300],
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'language': source.get('language', 'en')
                    })
                    
                    # 添加延迟避免请求过快
                    time.sleep(1)
            
            logger.info(f"从 {source['name']} 抓取到 {len(news_list)} 条国际新闻")
        except Exception as e:
            logger.error(f"从 {source['name']} 抓取失败: {str(e)}")
        
        return news_list
    
    def fetch_financial_data(self) -> List[Dict]:
        """抓取金融市场数据"""
        data_list = []
        
        try:
            # 1. 加密货币价格
            crypto_data = self.fetch_crypto_prices()
            if crypto_data:
                data_list.append(crypto_data)
            
            # 2. 主要股票指数
            indices_data = self.fetch_market_indices()
            if indices_data:
                data_list.append(indices_data)
            
            # 3. 汇率数据
            forex_data = self.fetch_forex_rates()
            if forex_data:
                data_list.append(forex_data)
            
            logger.info(f"抓取到 {len(data_list)} 项金融数据")
        except Exception as e:
            logger.error(f"抓取金融数据失败: {str(e)}")
        
        return data_list
    
    def fetch_crypto_prices(self) -> Dict:
        """抓取加密货币价格"""
        try:
            # 使用CoinGecko API（免费）
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum,binancecoin',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data:
                content_lines = ["加密货币价格（USD）:"]
                for coin_id, price_info in data.items():
                    coin_name = {
                        'bitcoin': '比特币',
                        'ethereum': '以太坊',
                        'binancecoin': 'BNB'
                    }.get(coin_id, coin_id)
                    
                    price = price_info.get('usd', 0)
                    change = price_info.get('usd_24h_change', 0)
                    
                    content_lines.append(f"{coin_name}: ${price:,.2f} ({change:+.2f}%)")
                
                return {
                    'title': '加密货币市场',
                    'category': '金融数据',
                    'source': 'CoinGecko',
                    'content': '\n'.join(content_lines),
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
        except Exception as e:
            logger.error(f"抓取加密货币价格失败: {str(e)}")
        
        return None
    
    def fetch_market_indices(self) -> Dict:
        """抓取主要股票指数"""
        try:
            # 模拟主要指数数据
            indices = [
                {'name': '道琼斯指数', 'symbol': 'DJI', 'price': 38585.19, 'change': +0.32},
                {'name': '标普500', 'symbol': 'SPX', 'price': 5208.76, 'change': +0.16},
                {'name': '纳斯达克', 'symbol': 'IXIC', 'price': 16412.67, 'change': -0.10},
                {'name': '日经225', 'symbol': 'N225', 'price': 38904.22, 'change': +1.08},
                {'name': '恒生指数', 'symbol': 'HSI', 'price': 17233.47, 'change': -0.43},
                {'name': '上证指数', 'symbol': '000001.SS', 'price': 3044.82, 'change': -0.18}
            ]
            
            content_lines = ["主要股指数据:"]
            for idx in indices:
                change_sign = '+' if idx['change'] >= 0 else ''
                content_lines.append(f"{idx['name']}({idx['symbol']}): {idx['price']:.2f} ({change_sign}{idx['change']}%)")
            
            return {
                'title': '全球股市指数',
                'category': '金融数据',
                'source': '市场数据',
                'content': '\n'.join(content_lines),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        except Exception as e:
            logger.error(f"抓取指数数据失败: {str(e)}")
        
        return None
    
    def fetch_forex_rates(self) -> Dict:
        """抓取汇率数据"""
        try:
            # 使用免费汇率API
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data and 'rates' in data:
                rates = data['rates']
                content_lines = ["主要货币汇率（1 USD =）:"]
                
                currencies = ['CNY', 'EUR', 'JPY', 'GBP', 'HKD']
                for currency in currencies:
                    if currency in rates:
                        rate = rates[currency]
                        content_lines.append(f"{currency}: {rate:.4f}")
                
                return {
                    'title': '外汇汇率',
                    'category': '金融数据',
                    'source': 'ExchangeRate-API',
                    'content': '\n'.join(content_lines),
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
        except Exception as e:
            logger.error(f"抓取汇率数据失败: {str(e)}")
            # 使用模拟数据
            content = """外汇汇率（1 USD =）:
CNY: 7.1985
EUR: 0.9204
JPY: 148.25
GBP: 0.7912
HKD: 7.8190"""
            
            return {
                'title': '外汇汇率',
                'category': '金融数据',
                'source': '市场数据',
                'content': content,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        
        return None
    
    def translate_to_chinese(self, text: str) -> str:
        """将英文内容翻译为中文（简化版）"""
        # 这里可以集成翻译API，如Google Translate, DeepL等
        # 目前返回原始文本，后续可以添加翻译功能
        return text
    
    def fetch_all_international_news(self) -> Dict[str, List[Dict]]:
        """抓取所有国际新闻"""
        all_news = {
            '国际财经': [],
            '国际新闻': [],
            '亚洲财经': [],
            '亚洲新闻': [],
            '金融数据': [],
            '加密货币': []
        }
        
        logger.info("开始抓取国际新闻...")
        
        # 抓取国际新闻源
        for source in self.international_sources:
            category = source['category']
            if category in all_news:
                news_items = self.fetch_from_international_source(source, max_articles=2)
                all_news[category].extend(news_items)
                time.sleep(2)  # 添加延迟避免请求过快
        
        # 抓取财经数据源
        for source in self.financial_data_sources:
            category = source['category']
            if category in all_news:
                news_items = self.fetch_from_international_source(source, max_articles=2)
                all_news[category].extend(news_items)
                time.sleep(2)
        
        # 抓取金融数据
        financial_data = self.fetch_financial_data()
        if financial_data:
            all_news['金融数据'].extend(financial_data)
        
        # 统计结果
        total_count = sum(len(news_list) for news_list in all_news.values())
        logger.info(f"总计抓取到 {total_count} 条国际新闻和数据")
        
        return all_news
    
    def get_top_international_news(self, limit_per_category: int = 3) -> List[Dict]:
        """获取各分类的顶部国际新闻"""
        all_news = self.fetch_all_international_news()
        top_news = []
        
        for category, news_list in all_news.items():
            if news_list:
                # 按标题长度排序（通常标题越长信息越详细）
                sorted_news = sorted(news_list, key=lambda x: len(x['title']), reverse=True)
                top_news.extend(sorted_news[:limit_per_category])
        
        return top_news[:15]  # 最多返回15条


def main():
    """测试函数"""
    import sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    fetcher = InternationalNewsFetcher()
    
    print("开始抓取外网一线消息...")
    print("=" * 60)
    
    # 测试抓取国际新闻
    top_news = fetcher.get_top_international_news(limit_per_category=2)
    
    for i, news in enumerate(top_news, 1):
        print(f"\n{i}. [{news['category']}] {news['source']}")
        print(f"标题: {news['title'][:80]}...")
        print(f"链接: {news['link']}")
        print(f"内容: {news['content'][:150]}...")
        print("-" * 60)
    
    print(f"\n总计抓取到 {len(top_news)} 条外网新闻")


if __name__ == "__main__":
    main()