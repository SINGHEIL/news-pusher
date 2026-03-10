#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from enhanced_news_fetcher import EnhancedNewsFetcher
    from enhanced_report_generator import EnhancedReportGenerator
    from wechat_notifier import WeChatNotifier
    
    logging.info('开始抓取新闻...')
    
    # 获取DeepSeek API密钥（免费）
    import os
    deepseek_key = os.getenv('DEEPSEEK_API_KEY', '')
    
    fetcher = EnhancedNewsFetcher(api_key=deepseek_key)
    
    logging.info('抓取所有新闻源...')
    all_news = fetcher.fetch_all_news()
    
    logging.info('生成简报...')
    generator = EnhancedReportGenerator()
    report = generator.filter_and_format(all_news)
    
    logging.info('初始化微信推送...')
    notifier_config = {
        'WECHAT_TEST': True,
        'WECHAT_TEST_APPID': os.getenv('WECHAT_TEST_APPID', ''),
        'WECHAT_TEST_SECRET': os.getenv('WECHAT_TEST_SECRET', ''),
        'WECHAT_TEST_TOUSER': os.getenv('WECHAT_TEST_TOUSER', ''),
    }
    notifier = WeChatNotifier(notifier_config)
    
    logging.info('推送到微信...')
    success = notifier.format_and_send(report)
    
    if success:
        logging.info('推送成功!')
        sys.exit(0)
    else:
        logging.error('推送失败!')
        sys.exit(1)
        
except Exception as e:
    logging.error(f'程序异常: {str(e)}', exc_info=True)
    sys.exit(1)
