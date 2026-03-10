#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from exam_news_fetcher import ExamNewsFetcher
    from content_filter import ContentFilter
    from wechat_notifier import WeChatNotifier
    
    logging.info('开始抓取新闻...')
    fetcher = ExamNewsFetcher()
    
    logging.info('筛选和格式化新闻...')
    filter = ContentFilter(use_ai=False)
    
    logging.info('初始化微信推送...')
    import os
    notifier_config = {
        'WECHAT_TEST': True,
        'WECHAT_TEST_APPID': os.getenv('WECHAT_TEST_APPID', ''),
        'WECHAT_TEST_SECRET': os.getenv('WECHAT_TEST_SECRET', ''),
        'WECHAT_TEST_TOUSER': os.getenv('WECHAT_TEST_TOUSER', ''),
    }
    notifier = WeChatNotifier(notifier_config)
    
    logging.info('抓取新闻...')
    all_news = fetcher.fetch_all_news()
    
    logging.info('筛选新闻...')
    filtered_news = filter.filter_news(all_news)
    
    logging.info('格式化报告...')
    report = filter.format_report(filtered_news)
    
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
