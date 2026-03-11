#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试国际新闻抓取功能
"""

import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_international_fetcher():
    """测试国际新闻抓取器"""
    try:
        logger.info("导入国际新闻抓取模块...")
        from international_news_fetcher import InternationalNewsFetcher
        
        logger.info("创建抓取器实例...")
        fetcher = InternationalNewsFetcher()
        
        logger.info("开始抓取国际新闻...")
        # 只测试前3个新闻源，避免请求过多
        test_sources = fetcher.international_sources[:3]
        
        all_news = []
        for source in test_sources:
            logger.info(f"测试抓取: {source['name']}")
            try:
                news_items = fetcher.fetch_from_international_source(source, max_articles=1)
                all_news.extend(news_items)
                logger.info(f"  成功抓取 {len(news_items)} 条新闻")
            except Exception as e:
                logger.warning(f"  抓取失败: {str(e)}")
        
        # 显示结果
        if all_news:
            logger.info("\n" + "="*60)
            logger.info(f"测试成功！共抓取到 {len(all_news)} 条国际新闻")
            logger.info("="*60)
            
            for i, news in enumerate(all_news, 1):
                logger.info(f"\n{i}. [{news['category']}] {news['source']}")
                logger.info(f"   标题: {news['title'][:80]}...")
                logger.info(f"   链接: {news['link']}")
                if 'content' in news and news['content']:
                    logger.info(f"   内容: {news['content'][:100]}...")
            
            return True
        else:
            logger.error("未能抓取到任何国际新闻")
            return False
            
    except ImportError as e:
        logger.error(f"模块导入失败: {str(e)}")
        logger.info("请检查依赖是否安装: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        return False

def test_financial_data():
    """测试金融数据抓取"""
    try:
        logger.info("\n测试金融数据抓取...")
        from international_news_fetcher import InternationalNewsFetcher
        
        fetcher = InternationalNewsFetcher()
        
        # 测试加密货币价格
        logger.info("测试加密货币价格抓取...")
        crypto_data = fetcher.fetch_crypto_prices()
        if crypto_data:
            logger.info(f"加密货币数据: {crypto_data['content'][:100]}...")
        
        # 测试汇率数据
        logger.info("测试汇率数据抓取...")
        forex_data = fetcher.fetch_forex_rates()
        if forex_data:
            logger.info(f"汇率数据: {forex_data['content'][:100]}...")
        
        return crypto_data is not None or forex_data is not None
        
    except Exception as e:
        logger.error(f"金融数据测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    logger.info("开始测试外网新闻抓取功能")
    logger.info("="*60)
    
    # 测试1: 国际新闻抓取
    news_success = test_international_fetcher()
    
    # 测试2: 金融数据抓取
    data_success = test_financial_data()
    
    # 总结
    logger.info("\n" + "="*60)
    logger.info("测试结果总结:")
    logger.info(f"国际新闻抓取: {'✅ 成功' if news_success else '❌ 失败'}")
    logger.info(f"金融数据抓取: {'✅ 成功' if data_success else '❌ 失败'}")
    
    if news_success or data_success:
        logger.info("\n🎉 外网新闻抓取功能测试通过！")
        logger.info("\n下一步操作:")
        logger.info("1. 运行完整推送: python run_global_push.py")
        logger.info("2. 查看详细指南: 外网新闻抓取指南.md")
        return 0
    else:
        logger.error("\n😞 外网新闻抓取功能测试失败")
        logger.info("\n可能的原因:")
        logger.info("1. 网络连接问题")
        logger.info("2. 新闻源网站改版")
        logger.info("3. 需要配置代理")
        return 1

if __name__ == "__main__":
    sys.exit(main())